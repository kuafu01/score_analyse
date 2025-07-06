import pyodbc

SQLSERVER_CONFIG = {
    'driver': 'ODBC Driver 17 for SQL Server',
    'server': 'localhost',
    'database': 'score_analyse'
}

def create_database_and_tables():
    # 连接到master数据库，创建数据库
    conn_str = (
        f"DRIVER={SQLSERVER_CONFIG['driver']};"
        f"SERVER={SQLSERVER_CONFIG['server']};"
        "DATABASE=master;"
        "Trusted_Connection=yes;"
    )
    conn = pyodbc.connect(conn_str, autocommit=True)
    cursor = conn.cursor()

    # 创建数据库（如果不存在）
    cursor.execute(f"""
    IF DB_ID('{SQLSERVER_CONFIG['database']}') IS NULL
        CREATE DATABASE [{SQLSERVER_CONFIG['database']}];
    """)
    print(f"数据库 {SQLSERVER_CONFIG['database']} 已创建或已存在。")
    cursor.close()
    conn.close()

    # 连接到新数据库，创建表
    conn_str_db = (
        f"DRIVER={SQLSERVER_CONFIG['driver']};"
        f"SERVER={SQLSERVER_CONFIG['server']};"
        f"DATABASE={SQLSERVER_CONFIG['database']};"
        "Trusted_Connection=yes;"
    )
    conn = pyodbc.connect(conn_str_db, autocommit=True)
    cursor = conn.cursor()

    # 先删除索引（如存在）
    drop_index_cmds = [
        "IF EXISTS (SELECT name FROM sys.indexes WHERE name = 'idx_exam_score_student_exam') DROP INDEX idx_exam_score_student_exam ON exam_score;",
        "IF EXISTS (SELECT name FROM sys.indexes WHERE name = 'idx_study_report_report_date') DROP INDEX idx_study_report_report_date ON study_report;"
    ]
    for cmd in drop_index_cmds:
        try:
            cursor.execute(cmd)
        except Exception as e:
            print(f"删除索引失败: {e}")


    # 先删除所有外键约束
    try:
        cursor.execute('''
        DECLARE @sql NVARCHAR(MAX) = N'';
        SELECT @sql += N'ALTER TABLE [' + OBJECT_SCHEMA_NAME(parent_object_id) + '].[' + OBJECT_NAME(parent_object_id) + '] DROP CONSTRAINT [' + name + '];\n'
        FROM sys.foreign_keys;
        EXEC sp_executesql @sql;
        ''')
        print("所有外键约束已删除。")
    except Exception as e:
        print(f"删除外键约束失败: {e}")

    # 再按外键依赖顺序删除表（如存在）
    drop_table_cmds = [
        "IF OBJECT_ID('push_comment', 'U') IS NOT NULL DROP TABLE push_comment;",
        "IF OBJECT_ID('class_push', 'U') IS NOT NULL DROP TABLE class_push;",
        "IF OBJECT_ID('teacher_class_subject', 'U') IS NOT NULL DROP TABLE teacher_class_subject;",
        "IF OBJECT_ID('study_report', 'U') IS NOT NULL DROP TABLE study_report;",
        "IF OBJECT_ID('exam_score', 'U') IS NOT NULL DROP TABLE exam_score;",
        "IF OBJECT_ID('class_exam_report', 'U') IS NOT NULL DROP TABLE class_exam_report;",
        "IF OBJECT_ID('schedule', 'U') IS NOT NULL DROP TABLE schedule;",
        "IF OBJECT_ID('exam', 'U') IS NOT NULL DROP TABLE exam;",
        "IF OBJECT_ID('student', 'U') IS NOT NULL DROP TABLE student;",
        "IF OBJECT_ID('class', 'U') IS NOT NULL DROP TABLE class;",
        "IF OBJECT_ID('teacher', 'U') IS NOT NULL DROP TABLE teacher;",
        "IF OBJECT_ID('subject', 'U') IS NOT NULL DROP TABLE subject;",
        "IF OBJECT_ID('[user]', 'U') IS NOT NULL DROP TABLE [user];",
        "IF OBJECT_ID('administrator', 'U') IS NOT NULL DROP TABLE administrator;"
    ]
    for cmd in drop_table_cmds:
        try:
            cursor.execute(cmd)
        except Exception as e:
            print(f"删除表失败: {e}")

    sql_commands = [
        '''CREATE TABLE administrator (
            cno VARCHAR(20) PRIMARY KEY,
            cname VARCHAR(20) NOT NULL
        )''',
        '''CREATE TABLE [user] (
            user_id VARCHAR(20) PRIMARY KEY,
            username VARCHAR(80) NOT NULL UNIQUE,
            password VARCHAR(120) NOT NULL,
            role VARCHAR(20) NOT NULL,
            name VARCHAR(50) NOT NULL,
            created_at DATETIME DEFAULT GETDATE()
        )''',
        '''CREATE TABLE subject (
            subject_id VARCHAR(10) PRIMARY KEY,
            subject_name VARCHAR(30) NOT NULL UNIQUE,
            department VARCHAR(20)
        )''',
        '''CREATE TABLE teacher (
            teacher_id VARCHAR(10) PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            gender VARCHAR(10) CHECK (gender IN ('男','女','其他')),
            title VARCHAR(20),
            subject_id VARCHAR(10),
            contact_email VARCHAR(50),
            office_address VARCHAR(100),
            phone VARCHAR(20),
            is_head_teacher BIT DEFAULT 0,
            created_at DATETIME DEFAULT GETDATE(),
            FOREIGN KEY (subject_id) REFERENCES subject(subject_id)
        )''',
        '''CREATE TABLE class (
            class_id VARCHAR(10) PRIMARY KEY,
            class_name VARCHAR(30) NOT NULL,
            head_teacher_id VARCHAR(10) NOT NULL,
            grade_level VARCHAR(10),
            FOREIGN KEY (head_teacher_id) REFERENCES teacher(teacher_id)
        )''',
        '''CREATE TABLE student (
            student_id VARCHAR(10) PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            gender VARCHAR(10) CHECK (gender IN ('男','女','其他')),
            birth_date DATE,
            nation VARCHAR(20),
            province VARCHAR(20),
            political_status VARCHAR(10) CHECK (political_status IN ('群众','团员')),
            class_id VARCHAR(10) NOT NULL,
            contact_phone VARCHAR(20),
            emergency_contact VARCHAR(50),
            created_at DATETIME DEFAULT GETDATE(),
            FOREIGN KEY (class_id) REFERENCES class(class_id)
        )''',
        '''CREATE TABLE exam (
            exam_id VARCHAR(10) PRIMARY KEY,
            exam_name VARCHAR(50) NOT NULL,
            exam_type VARCHAR(10) CHECK (exam_type IN ('期中','期末','模拟','月考')),
            exam_date DATE NOT NULL
        )''',
        '''CREATE TABLE exam_score (
            score_id VARCHAR(20) PRIMARY KEY,
            student_id VARCHAR(10) NOT NULL,
            exam_id VARCHAR(10) NOT NULL,
            subject_id VARCHAR(10) NOT NULL,
            score DECIMAL(5,2) CHECK (score >= 0 AND score <= 100),
            ranking INT,
            created_at DATE,
            FOREIGN KEY (student_id) REFERENCES student(student_id),
            FOREIGN KEY (exam_id) REFERENCES exam(exam_id),
            FOREIGN KEY (subject_id) REFERENCES subject(subject_id)
        )''',
        '''CREATE TABLE study_report (
            report_id VARCHAR(20) PRIMARY KEY,
            student_id VARCHAR(10) NOT NULL,
            teacher_id VARCHAR(10) NOT NULL,
            report_date DATE NOT NULL,
            content TEXT,
            evaluation_level CHAR(1) CHECK (evaluation_level IN ('A','B','C','D')),
            FOREIGN KEY (student_id) REFERENCES student(student_id),
            FOREIGN KEY (teacher_id) REFERENCES teacher(teacher_id)
        )''',
        '''CREATE TABLE teacher_class_subject (
            relation_id VARCHAR(20) PRIMARY KEY,
            teacher_id VARCHAR(10) NOT NULL,
            class_id VARCHAR(10) NOT NULL,
            subject_id VARCHAR(10) NOT NULL,
            CONSTRAINT UQ_teacher_class_subject UNIQUE (teacher_id, class_id, subject_id),
            FOREIGN KEY (teacher_id) REFERENCES teacher(teacher_id),
            FOREIGN KEY (class_id) REFERENCES class(class_id),
            FOREIGN KEY (subject_id) REFERENCES subject(subject_id)
        )''',
        '''CREATE TABLE class_exam_report (
            report_id VARCHAR(20) PRIMARY KEY,
            teacher_id VARCHAR(10) NOT NULL,
            class_id VARCHAR(10) NOT NULL,
            exam_id VARCHAR(10) NOT NULL,
            content TEXT,
            created_at DATETIME DEFAULT GETDATE(),
            updated_at DATETIME DEFAULT GETDATE(),
            FOREIGN KEY (teacher_id) REFERENCES teacher(teacher_id),
            FOREIGN KEY (class_id) REFERENCES class(class_id),
            FOREIGN KEY (exam_id) REFERENCES exam(exam_id),
            CONSTRAINT UQ_class_exam_report UNIQUE (teacher_id, class_id, exam_id)
        )''',
        '''CREATE TABLE schedule (
            schedule_id INT IDENTITY(1,1) PRIMARY KEY,
            class_id VARCHAR(10) NOT NULL,
            week_day INT NOT NULL CHECK (week_day BETWEEN 1 AND 7), -- 1=周一, 7=周日
            period INT NOT NULL CHECK (period BETWEEN 1 AND 8), -- 1-4上午, 5-8下午
            subject_id VARCHAR(10) NOT NULL,
            teacher_id VARCHAR(10) NOT NULL,
            classroom VARCHAR(30),
            remark VARCHAR(100),
            CONSTRAINT UQ_schedule UNIQUE (class_id, week_day, period),
            FOREIGN KEY (class_id) REFERENCES class(class_id),
            FOREIGN KEY (subject_id) REFERENCES subject(subject_id),
            FOREIGN KEY (teacher_id) REFERENCES teacher(teacher_id)
        )''',
        'CREATE INDEX idx_exam_score_student_exam ON exam_score(student_id, exam_id);',
        'CREATE INDEX idx_study_report_report_date ON study_report(report_date);'
    ]

    for cmd in sql_commands:
        try:
            cursor.execute(cmd)
            print(f"执行成功: {cmd.split('(')[0].strip()}")
        except Exception as e:
            print(f"执行失败: {e}")
    cursor.close()
    conn.close()


# ================== 推送/评论功能相关表结构 ==================
def create_push_and_comment_tables():
    conn_str = (
        f"DRIVER={SQLSERVER_CONFIG['driver']};"
        f"SERVER={SQLSERVER_CONFIG['server']};"
        f"DATABASE={SQLSERVER_CONFIG['database']};"
        "Trusted_Connection=yes;"
    )
    conn = pyodbc.connect(conn_str, autocommit=True)
    cursor = conn.cursor()
    # 创建推送表 class_push
    try:
        cursor.execute('''
            IF OBJECT_ID('class_push', 'U') IS NULL
            CREATE TABLE class_push (
                push_id VARCHAR(32) PRIMARY KEY,
                class_id VARCHAR(20),
                publisher_id VARCHAR(20),
                publisher_role VARCHAR(20),
                title TEXT,
                content TEXT,
                push_type VARCHAR(20),
                is_top INT,
                top_expire DATETIME,
                attachment_path TEXT,
                create_time DATETIME
            )
        ''')
        print('class_push 表已创建或已存在。')
    except Exception as e:
        print(f'class_push 表创建失败: {e}')
    # 创建评论表 push_comment
    try:
        cursor.execute('''
            IF OBJECT_ID('push_comment', 'U') IS NULL
            CREATE TABLE push_comment (
                comment_id VARCHAR(32) PRIMARY KEY,
                push_id VARCHAR(32),
                user_id VARCHAR(20),
                user_role VARCHAR(20),
                content TEXT,
                create_time DATETIME
            )
        ''')
        print('push_comment 表已创建或已存在。')
    except Exception as e:
        print(f'push_comment 表创建失败: {e}')
    cursor.close()
    conn.close()

if __name__ == '__main__':
    create_database_and_tables()
    create_push_and_comment_tables()
