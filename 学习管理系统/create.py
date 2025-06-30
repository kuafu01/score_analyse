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

    # 再按外键依赖顺序删除表（如存在）
    drop_table_cmds = [
        "IF OBJECT_ID('teacher_class_subject', 'U') IS NOT NULL DROP TABLE teacher_class_subject;",
        "IF OBJECT_ID('study_report', 'U') IS NOT NULL DROP TABLE study_report;",
        "IF OBJECT_ID('exam_score', 'U') IS NOT NULL DROP TABLE exam_score;",
        "IF OBJECT_ID('exam', 'U') IS NOT NULL DROP TABLE exam;",
        "IF OBJECT_ID('student', 'U') IS NOT NULL DROP TABLE student;",
        "IF OBJECT_ID('class', 'U') IS NOT NULL DROP TABLE class;",
        "IF OBJECT_ID('teacher', 'U') IS NOT NULL DROP TABLE teacher;",
        "IF OBJECT_ID('subject', 'U') IS NOT NULL DROP TABLE subject;",
        "IF OBJECT_ID('[user]', 'U') IS NOT NULL DROP TABLE [user];"
    ]
    for cmd in drop_table_cmds:
        try:
            cursor.execute(cmd)
        except Exception as e:
            print(f"删除表失败: {e}")

    sql_commands = [
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
            title VARCHAR(20),
            subject_id VARCHAR(10),
            contact_email VARCHAR(50),
            is_head_teacher BIT DEFAULT 0,
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

if __name__ == '__main__':
    create_database_and_tables()
