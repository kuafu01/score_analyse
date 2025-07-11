import pyodbc

SQLSERVER_CONFIG = {
    'driver': 'ODBC Driver 17 for SQL Server',
    'server': 'localhost',
    'database': 'score_analyse'
}

def get_conn():
    conn_str = (
        f"DRIVER={SQLSERVER_CONFIG['driver']};"
        f"SERVER={SQLSERVER_CONFIG['server']};"
        f"DATABASE={SQLSERVER_CONFIG['database']};"
        "Trusted_Connection=yes;"
    )
    return pyodbc.connect(conn_str)

def insert_test_data():
    conn = get_conn()
    cursor = conn.cursor()
    # 先禁用所有外键约束
    cursor.execute('EXEC sp_msforeachtable "ALTER TABLE ? NOCHECK CONSTRAINT all"')
    # 清空所有表（按依赖顺序，先删子表再删父表）
    cursor.execute('DELETE FROM teacher_class_subject')
    cursor.execute('DELETE FROM study_report')
    cursor.execute('DELETE FROM exam_score')
    cursor.execute('DELETE FROM schedule')
    cursor.execute('DELETE FROM exam')
    cursor.execute('DELETE FROM student')
    cursor.execute('DELETE FROM class')
    cursor.execute('DELETE FROM teacher')
    cursor.execute('DELETE FROM subject')
    cursor.execute('DELETE FROM [user]')
    cursor.execute('DELETE FROM administrator')
    conn.commit()
    # 再恢复所有外键约束
    cursor.execute('EXEC sp_msforeachtable "ALTER TABLE ? WITH CHECK CHECK CONSTRAINT all"')

    # 1. 学科
    subjects = [
        ('c0001', '语文', '文科'),
        ('c0002', '数学', '理科'),
        ('c0003', '英语', '外语'),
        ('c0004', '物理', '理科'),
        ('c0005', '化学', '理科'),
        ('c0006', '生物', '理科'),
        ('c0007', '历史', '文科'),
        ('c0008', '地理', '文科'),
        ('c0009', '政治', '文科'),
        ('c0010', '体育', '综合')
    ]
    for sid, name, dept in subjects:
        cursor.execute("INSERT INTO subject (subject_id, subject_name, department) VALUES (?, ?, ?)", sid, name, dept)

    # 2. 教师
    teachers = [
        # 工号, 姓名, 性别, 职称, 学科, 邮箱, 办公室, 电话, 是否班主任
        ('t0001', '张老师', '男', '语文教师', 'c0001', 't0001@school.edu', 'A101', '13900010001', 1),
        ('t0002', '李老师', '女', '数学教师', 'c0002', 't0002@school.edu', 'A102', '13900010002', 1),
        ('t0003', '王老师', '男', '英语教师', 'c0003', 't0003@school.edu', 'A103', '13900010003', 1),
        ('t0004', '刘老师', '男', '物理教师', 'c0004', 't0004@school.edu', 'B201', '13900010004', 0),
        ('t0005', '陈老师', '女', '化学教师', 'c0005', 't0005@school.edu', 'B202', '13900010005', 0),
        ('t0006', '赵老师', '女', '生物教师', 'c0006', 't0006@school.edu', 'B203', '13900010006', 0),
        ('t0007', '孙老师', '男', '历史教师', 'c0007', 't0007@school.edu', 'C301', '13900010007', 0),
        ('t0008', '周老师', '女', '地理教师', 'c0008', 't0008@school.edu', 'C302', '13900010008', 0),
        ('t0009', '吴老师', '男', '政治教师', 'c0009', 't0009@school.edu', 'C303', '13900010009', 0),
        ('t0010', '郑老师', '男', '体育教师', 'c0010', 't0010@school.edu', 'D401', '13900010010', 0)
    ]
    for tid, name, gender, title, subid, email, office, phone, is_head in teachers:
        cursor.execute("INSERT INTO teacher (teacher_id, name, gender, title, subject_id, contact_email, office_address, phone, is_head_teacher) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", tid, name, gender, title, subid, email, office, phone, is_head)

    # 3. 班级
    classes = [
        ('cl001', '高一(1)班', 't0001', '高一'),
        ('cl002', '高一(2)班', 't0002', '高一'),
        ('cl003', '高一(3)班', 't0003', '高一')
    ]
    for cid, cname, head_tid, grade in classes:
        cursor.execute("INSERT INTO class (class_id, class_name, head_teacher_id, grade_level) VALUES (?, ?, ?, ?)", cid, cname, head_tid, grade)

    # 4. 学生
    students = [
        # 学号, 姓名, 性别, 出生日期, 民族, 省份, 政治面貌, 班级, 联系电话, 紧急联系人
        ('s0001', '张三', '男', '2008-03-15', '汉族', '江苏', '团员', 'cl001', '13800138001', '张父-13900139001'),
        ('s0002', '李四', '男', '2008-05-22', '回族', '山东', '群众', 'cl001', '13800138002', '李母-13900139002'),
        ('s0003', '王芳', '女', '2008-02-10', '汉族', '浙江', '团员', 'cl001', '13800138003', '王父-13900139003'),
        ('s0004', '赵敏', '女', '2008-07-30', '满族', '辽宁', '群众', 'cl002', '13800138004', '赵母-13900139004'),
        ('s0005', '刘强', '男', '2008-11-05', '汉族', '安徽', '团员', 'cl002', '13800138005', '刘父-13900139005'),
        ('s0006', '陈雪', '女', '2007-09-18', '壮族', '广西', '群众', 'cl003', '13800138006', '陈母-13900139006'),
        ('s0007', '杨帆', '男', '2007-04-25', '汉族', '四川', '团员', 'cl003', '13800138007', '杨父-13900139007'),
        ('s0008', '周婷', '女', '2007-12-12', '汉族', '湖北', '群众', 'cl003', '13800138008', '周母-13900139008'),
        ('s0009', '吴昊', '男', '2007-08-08', '土家族', '湖南', '团员', 'cl003', '13800138009', '吴父-13900139009'),
        ('s0010', '郑阳', '男', '2007-06-20', '汉族', '江西', '群众', 'cl003', '13800138010', '郑母-13900139010'),
        # 新增学生
        ('s0011', '林浩', '男', '2008-01-10', '汉族', '江苏', '团员', 'cl001', '13800138011', '林父-13900139011'),
        ('s0012', '周悦', '女', '2008-02-18', '汉族', '江苏', '群众', 'cl001', '13800138012', '周母-13900139012'),
        ('s0013', '许明', '男', '2008-03-22', '汉族', '江苏', '团员', 'cl001', '13800138013', '许父-13900139013'),
        ('s0014', '宋倩', '女', '2008-04-15', '汉族', '江苏', '群众', 'cl001', '13800138014', '宋母-13900139014'),
        ('s0015', '高翔', '男', '2008-05-09', '汉族', '江苏', '团员', 'cl001', '13800138015', '高父-13900139015'),
        ('s0016', '李婷', '女', '2008-06-03', '汉族', '江苏', '群众', 'cl001', '13800138016', '李母-13900139016'),
        ('s0017', '王磊', '男', '2008-07-27', '汉族', '江苏', '团员', 'cl001', '13800138017', '王父-13900139017')
    ]
    for sid, name, gender, birth, nation, province, political, cid, phone, emer in students:
        cursor.execute("INSERT INTO student (student_id, name, gender, birth_date, nation, province, political_status, class_id, contact_phone, emergency_contact) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", sid, name, gender, birth, nation, province, political, cid, phone, emer)

    # 5. 用户
    users = [
        # 学生
        ('u0001', 's0001', '123456', 'student', '张三'),
        ('u0002', 's0002', '123456', 'student', '李四'),
        ('u0003', 's0003', '123456', 'student', '王芳'),
        ('u0004', 's0004', '123456', 'student', '赵敏'),
        ('u0005', 's0005', '123456', 'student', '刘强'),
        ('u0006', 's0006', '123456', 'student', '陈雪'),
        ('u0007', 's0007', '123456', 'student', '杨帆'),
        ('u0008', 's0008', '123456', 'student', '周婷'),
        ('u0009', 's0009', '123456', 'student', '吴昊'),
        ('u0010', 's0010', '123456', 'student', '郑阳'),
        # 教师
        ('u0011', 't0001', '123456', 'classmaster', '张老师'),
        ('u0012', 't0002', '123456', 'classmaster', '李老师'),
        ('u0013', 't0003', '123456', 'classmaster', '王老师'),
        ('u0014', 't0004', '123456', 'teacher', '刘老师'),
        ('u0015', 't0005', '123456', 'teacher', '陈老师'),
        ('u0016', 't0006', '123456', 'teacher', '赵老师'),
        ('u0017', 't0007', '123456', 'teacher', '孙老师'),
        ('u0018', 't0008', '123456', 'teacher', '周老师'),
        ('u0019', 't0009', '123456', 'teacher', '吴老师'),
        ('u0020', 't0010', '123456', 'teacher', '郑老师'),
        # 管理员
        ('u9001', 'admin01', 'admin123', 'admin', '系统管理员')
    ]
    for uid, uname, pwd, role, name in users:
        cursor.execute("INSERT INTO [user] (user_id, username, password, role, name) VALUES (?, ?, ?, ?, ?)", uid, uname, pwd, role, name)
    # 管理员表数据
    cursor.execute("INSERT INTO administrator (cno, cname) VALUES (?, ?)", 'admin01', '系统管理员')

    # 6. 考试
    exams = [
        ('ex001', '2025学年期中考试', '期中', '2025-04-10'),
        ('ex002', '2025学年期末考试', '期末', '2025-06-20'),
        ('ex003', '2025年3月月考', '月考', '2025-03-05'),
        ('ex004', '2025年5月月考', '月考', '2025-05-08'),
        ('ex005', '2025高考模拟考', '模拟', '2025-05-25')
    ]
    for eid, ename, etype, edate in exams:
        cursor.execute("INSERT INTO exam (exam_id, exam_name, exam_type, exam_date) VALUES (?, ?, ?, ?)", eid, ename, etype, edate)

    # 7. 部分考试成绩
    scores = [
        # s0001
        ('sc0001', 's0001', 'ex001', 'c0001', 85.5, 3, '2025-04-10'),
        ('sc0002', 's0001', 'ex001', 'c0002', 92.0, 1, '2025-04-10'),
        ('sc0003', 's0001', 'ex001', 'c0003', 78.0, 5, '2025-04-10'),
        ('sc0004', 's0001', 'ex002', 'c0001', 88.0, 2, '2025-06-20'),
        ('sc0005', 's0001', 'ex002', 'c0002', 94.5, 1, '2025-06-20'),
        ('sc0015', 's0001', 'ex001', 'c0004', 87.5, 4, '2025-04-10'),
        ('sc0016', 's0001', 'ex001', 'c0005', 85.0, 5, '2025-04-10'),
        ('sc0017', 's0001', 'ex001', 'c0006', 88.0, 3, '2025-04-10'),
        ('sc0018', 's0001', 'ex001', 'c0007', 92.5, 2, '2025-04-10'),
        ('sc0019', 's0001', 'ex001', 'c0008', 89.0, 4, '2025-04-10'),
        ('sc0020', 's0001', 'ex001', 'c0009', 91.0, 3, '2025-04-10'),
        ('sc0021', 's0001', 'ex001', 'c0010', 94.0, 1, '2025-04-10'),
        ('sc0022', 's0001', 'ex002', 'c0003', 83.5, 5, '2025-06-20'),
        ('sc0023', 's0001', 'ex002', 'c0004', 86.0, 4, '2025-06-20'),
        ('sc0024', 's0001', 'ex002', 'c0005', 88.5, 3, '2025-06-20'),
        ('sc0025', 's0001', 'ex002', 'c0006', 90.0, 2, '2025-06-20'),
        ('sc0026', 's0001', 'ex002', 'c0007', 92.0, 1, '2025-06-20'),
        ('sc0027', 's0001', 'ex002', 'c0008', 87.0, 3, '2025-06-20'),
        ('sc0028', 's0001', 'ex002', 'c0009', 89.5, 2, '2025-06-20'),
        ('sc0029', 's0001', 'ex002', 'c0010', 93.5, 1, '2025-06-20'),
        ('sc0030', 's0001', 'ex003', 'c0001', 84.0, 4, '2025-03-05'),
        ('sc0031', 's0001', 'ex003', 'c0002', 89.5, 3, '2025-03-05'),
        ('sc0032', 's0001', 'ex003', 'c0003', 82.0, 5, '2025-03-05'),
        ('sc0033', 's0001', 'ex003', 'c0004', 86.5, 4, '2025-03-05'),
        ('sc0034', 's0001', 'ex003', 'c0005', 88.0, 3, '2025-03-05'),
        ('sc0035', 's0001', 'ex003', 'c0006', 91.5, 2, '2025-03-05'),
        ('sc0036', 's0001', 'ex003', 'c0007', 93.0, 1, '2025-03-05'),
        ('sc0037', 's0001', 'ex003', 'c0008', 87.5, 3, '2025-03-05'),
        ('sc0038', 's0001', 'ex003', 'c0009', 90.0, 2, '2025-03-05'),
        ('sc0039', 's0001', 'ex003', 'c0010', 94.5, 1, '2025-03-05'),
        ('sc0040', 's0001', 'ex004', 'c0001', 85.5, 4, '2025-05-08'),
        ('sc0041', 's0001', 'ex004', 'c0002', 90.0, 3, '2025-05-08'),
        ('sc0042', 's0001', 'ex004', 'c0003', 83.0, 5, '2025-05-08'),
        ('sc0043', 's0001', 'ex004', 'c0004', 88.0, 4, '2025-05-08'),
        ('sc0044', 's0001', 'ex004', 'c0005', 89.5, 3, '2025-05-08'),
        ('sc0045', 's0001', 'ex004', 'c0006', 92.0, 2, '2025-05-08'),
        ('sc0046', 's0001', 'ex004', 'c0007', 94.0, 1, '2025-05-08'),
        ('sc0047', 's0001', 'ex004', 'c0008', 86.5, 4, '2025-05-08'),
        ('sc0048', 's0001', 'ex004', 'c0009', 91.0, 3, '2025-05-08'),
        ('sc0049', 's0001', 'ex004', 'c0010', 95.0, 1, '2025-05-08'),
        ('sc0050', 's0001', 'ex005', 'c0001', 86.0, 4, '2025-05-25'),
        ('sc0051', 's0001', 'ex005', 'c0002', 91.5, 3, '2025-05-25'),
        ('sc0052', 's0001', 'ex005', 'c0003', 84.5, 5, '2025-05-25'),
        ('sc0053', 's0001', 'ex005', 'c0004', 89.0, 4, '2025-05-25'),
        ('sc0054', 's0001', 'ex005', 'c0005', 90.5, 3, '2025-05-25'),
        ('sc0055', 's0001', 'ex005', 'c0006', 93.0, 2, '2025-05-25'),
        ('sc0056', 's0001', 'ex005', 'c0007', 95.0, 1, '2025-05-25'),
        ('sc0057', 's0001', 'ex005', 'c0008', 88.0, 4, '2025-05-25'),
        ('sc0058', 's0001', 'ex005', 'c0009', 92.5, 3, '2025-05-25'),
        ('sc0059', 's0001', 'ex005', 'c0010', 96.0, 1, '2025-05-25'),
        # s0002
        ('sc0006', 's0002', 'ex001', 'c0001', 90.0, 2, '2025-04-10'),
        ('sc0007', 's0002', 'ex001', 'c0002', 88.5, 3, '2025-04-10'),
        ('sc0008', 's0002', 'ex002', 'c0001', 92.5, 1, '2025-06-20'),
        ('sc0009', 's0002', 'ex002', 'c0002', 90.0, 2, '2025-06-20'),
        # s0005
        ('sc0201', 's0005', 'ex001', 'c0001', 60.0, 8, '2025-04-10'),
        ('sc0202', 's0005', 'ex001', 'c0002', 95.0, 1, '2025-04-10'),
        ('sc0203', 's0005', 'ex001', 'c0003', 70.0, 7, '2025-04-10'),
        ('sc0204', 's0005', 'ex001', 'c0004', 88.0, 3, '2025-04-10'),
        ('sc0205', 's0005', 'ex001', 'c0005', 90.0, 2, '2025-04-10'),
        ('sc0206', 's0005', 'ex001', 'c0006', 85.0, 4, '2025-04-10'),
        ('sc0207', 's0005', 'ex001', 'c0007', 92.0, 1, '2025-04-10'),
        ('sc0208', 's0005', 'ex001', 'c0008', 60.0, 8, '2025-04-10'),
        ('sc0209', 's0005', 'ex001', 'c0009', 95.0, 1, '2025-04-10'),
        ('sc0210', 's0005', 'ex001', 'c0010', 70.0, 7, '2025-04-10'),
        ('sc0211', 's0005', 'ex002', 'c0001', 88.0, 3, '2025-06-20'),
        ('sc0212', 's0005', 'ex002', 'c0002', 90.0, 2, '2025-06-20'),
        ('sc0213', 's0005', 'ex002', 'c0003', 85.0, 4, '2025-06-20'),
        ('sc0214', 's0005', 'ex002', 'c0004', 92.0, 1, '2025-06-20'),
        ('sc0215', 's0005', 'ex002', 'c0005', 60.0, 8, '2025-06-20'),
        ('sc0216', 's0005', 'ex002', 'c0006', 95.0, 1, '2025-06-20'),
        ('sc0217', 's0005', 'ex002', 'c0007', 70.0, 7, '2025-06-20'),
        ('sc0218', 's0005', 'ex002', 'c0008', 88.0, 3, '2025-06-20'),
        ('sc0219', 's0005', 'ex002', 'c0009', 90.0, 2, '2025-06-20'),
        ('sc0220', 's0005', 'ex002', 'c0010', 85.0, 4, '2025-06-20'),
        # s0006
        ('sc0301', 's0006', 'ex001', 'c0001', 95.0, 1, '2025-04-10'),
        ('sc0302', 's0006', 'ex001', 'c0002', 60.0, 8, '2025-04-10'),
        ('sc0303', 's0006', 'ex001', 'c0003', 88.0, 3, '2025-04-10'),
        ('sc0304', 's0006', 'ex001', 'c0004', 90.0, 2, '2025-04-10'),
        ('sc0305', 's0006', 'ex001', 'c0005', 85.0, 4, '2025-04-10'),
        ('sc0306', 's0006', 'ex001', 'c0006', 92.0, 1, '2025-04-10'),
        ('sc0307', 's0006', 'ex001', 'c0007', 70.0, 7, '2025-04-10'),
        ('sc0308', 's0006', 'ex001', 'c0008', 88.0, 3, '2025-04-10'),
        ('sc0309', 's0006', 'ex001', 'c0009', 90.0, 2, '2025-04-10'),
        ('sc0310', 's0006', 'ex001', 'c0010', 85.0, 4, '2025-04-10'),
        ('sc0311', 's0006', 'ex002', 'c0001', 60.0, 8, '2025-06-20'),
        ('sc0312', 's0006', 'ex002', 'c0002', 95.0, 1, '2025-06-20'),
        ('sc0313', 's0006', 'ex002', 'c0003', 70.0, 7, '2025-06-20'),
        ('sc0314', 's0006', 'ex002', 'c0004', 88.0, 3, '2025-06-20'),
        ('sc0315', 's0006', 'ex002', 'c0005', 90.0, 2, '2025-06-20'),
        ('sc0316', 's0006', 'ex002', 'c0006', 85.0, 4, '2025-06-20'),
        ('sc0317', 's0006', 'ex002', 'c0007', 92.0, 1, '2025-06-20'),
        ('sc0318', 's0006', 'ex002', 'c0008', 60.0, 8, '2025-06-20'),
        ('sc0319', 's0006', 'ex002', 'c0009', 95.0, 1, '2025-06-20'),
        ('sc0320', 's0006', 'ex002', 'c0010', 70.0, 7, '2025-06-20'),
        # s0007
        ('sc0401', 's0007', 'ex001', 'c0001', 70.0, 7, '2025-04-10'),
        ('sc0402', 's0007', 'ex001', 'c0002', 88.0, 3, '2025-04-10'),
        ('sc0403', 's0007', 'ex001', 'c0003', 90.0, 2, '2025-04-10'),
        ('sc0404', 's0007', 'ex001', 'c0004', 85.0, 4, '2025-04-10'),
        ('sc0405', 's0007', 'ex001', 'c0005', 92.0, 1, '2025-04-10'),
        ('sc0406', 's0007', 'ex001', 'c0006', 60.0, 8, '2025-04-10'),
        ('sc0407', 's0007', 'ex001', 'c0007', 88.0, 3, '2025-04-10'),
        ('sc0408', 's0007', 'ex001', 'c0008', 90.0, 2, '2025-04-10'),
        ('sc0409', 's0007', 'ex001', 'c0009', 85.0, 4, '2025-04-10'),
        ('sc0410', 's0007', 'ex001', 'c0010', 92.0, 1, '2025-04-10'),
        ('sc0411', 's0007', 'ex002', 'c0001', 88.0, 3, '2025-06-20'),
        ('sc0412', 's0007', 'ex002', 'c0002', 60.0, 8, '2025-06-20'),
        ('sc0413', 's0007', 'ex002', 'c0003', 95.0, 1, '2025-06-20'),
        ('sc0414', 's0007', 'ex002', 'c0004', 70.0, 7, '2025-06-20'),
        ('sc0415', 's0007', 'ex002', 'c0005', 88.0, 3, '2025-06-20'),
        ('sc0416', 's0007', 'ex002', 'c0006', 90.0, 2, '2025-06-20'),
        ('sc0417', 's0007', 'ex002', 'c0007', 85.0, 4, '2025-06-20'),
        ('sc0418', 's0007', 'ex002', 'c0008', 92.0, 1, '2025-06-20'),
        ('sc0419', 's0007', 'ex002', 'c0009', 70.0, 7, '2025-06-20'),
        ('sc0420', 's0007', 'ex002', 'c0010', 88.0, 3, '2025-06-20'),
        # s0008
        ('sc0501', 's0008', 'ex001', 'c0001', 88.0, 3, '2025-04-10'),
        ('sc0502', 's0008', 'ex001', 'c0002', 90.0, 2, '2025-04-10'),
        ('sc0503', 's0008', 'ex001', 'c0003', 85.0, 4, '2025-04-10'),
        ('sc0504', 's0008', 'ex001', 'c0004', 92.0, 1, '2025-04-10'),
        ('sc0505', 's0008', 'ex001', 'c0005', 60.0, 8, '2025-04-10'),
        ('sc0506', 's0008', 'ex001', 'c0006', 95.0, 1, '2025-04-10'),
        ('sc0507', 's0008', 'ex001', 'c0007', 70.0, 7, '2025-04-10'),
        ('sc0508', 's0008', 'ex001', 'c0008', 88.0, 3, '2025-04-10'),
        ('sc0509', 's0008', 'ex001', 'c0009', 90.0, 2, '2025-04-10'),
        ('sc0510', 's0008', 'ex001', 'c0010', 85.0, 4, '2025-04-10'),
        ('sc0511', 's0008', 'ex002', 'c0001', 92.0, 1, '2025-06-20'),
        ('sc0512', 's0008', 'ex002', 'c0002', 88.0, 3, '2025-06-20'),
        ('sc0513', 's0008', 'ex002', 'c0003', 90.0, 2, '2025-06-20'),
        ('sc0514', 's0008', 'ex002', 'c0004', 85.0, 4, '2025-06-20'),
        ('sc0515', 's0008', 'ex002', 'c0005', 92.0, 1, '2025-06-20'),
        ('sc0516', 's0008', 'ex002', 'c0006', 60.0, 8, '2025-06-20'),
        ('sc0517', 's0008', 'ex002', 'c0007', 95.0, 1, '2025-06-20'),
        ('sc0518', 's0008', 'ex002', 'c0008', 70.0, 7, '2025-06-20'),
        ('sc0519', 's0008', 'ex002', 'c0009', 88.0, 3, '2025-06-20'),
        ('sc0520', 's0008', 'ex002', 'c0010', 90.0, 2, '2025-06-20'),
        # s0009
        ('sc0601', 's0009', 'ex001', 'c0001', 60.0, 8, '2025-04-10'),
        ('sc0602', 's0009', 'ex001', 'c0002', 95.0, 1, '2025-04-10'),
        ('sc0603', 's0009', 'ex001', 'c0003', 70.0, 7, '2025-04-10'),
        ('sc0604', 's0009', 'ex001', 'c0004', 88.0, 3, '2025-04-10'),
        ('sc0605', 's0009', 'ex001', 'c0005', 90.0, 2, '2025-04-10'),
        ('sc0606', 's0009', 'ex001', 'c0006', 85.0, 4, '2025-04-10'),
        ('sc0607', 's0009', 'ex001', 'c0007', 92.0, 1, '2025-04-10'),
        ('sc0608', 's0009', 'ex001', 'c0008', 60.0, 8, '2025-04-10'),
        ('sc0609', 's0009', 'ex001', 'c0009', 95.0, 1, '2025-04-10'),
        ('sc0610', 's0009', 'ex001', 'c0010', 70.0, 7, '2025-04-10'),
        ('sc0611', 's0009', 'ex002', 'c0001', 88.0, 3, '2025-06-20'),
        ('sc0612', 's0009', 'ex002', 'c0002', 90.0, 2, '2025-06-20'),
        ('sc0613', 's0009', 'ex002', 'c0003', 85.0, 4, '2025-06-20'),
        ('sc0614', 's0009', 'ex002', 'c0004', 92.0, 1, '2025-06-20'),
        ('sc0615', 's0009', 'ex002', 'c0005', 60.0, 8, '2025-06-20'),
        ('sc0616', 's0009', 'ex002', 'c0006', 95.0, 1, '2025-06-20'),
        ('sc0617', 's0009', 'ex002', 'c0007', 70.0, 7, '2025-06-20'),
        ('sc0618', 's0009', 'ex002', 'c0008', 88.0, 3, '2025-06-20'),
        ('sc0619', 's0009', 'ex002', 'c0009', 90.0, 2, '2025-06-20'),
        ('sc0620', 's0009', 'ex002', 'c0010', 85.0, 4, '2025-06-20'),
        # s0010
        ('sc0010', 's0010', 'ex005', 'c0010', 95.0, 1, '2025-05-25'),
        # 可继续补充s0010所有考试所有学科成绩
        # s0010所有考试所有学科成绩
        # ex001-ex005, c0001-c0010
        *[(f'sc10010{ei}{si}', 's0010', exid, f'c{str(1+si).zfill(4)}', min(100, 60+10*ei+si), 10-si, date) for ei, (exid, date) in enumerate([
            ('ex001','2025-04-10'),('ex002','2025-06-20'),('ex003','2025-03-05'),('ex004','2025-05-08'),('ex005','2025-05-25')]) for si in range(10)],

        # 新增学生s0011-s0017，ex001和ex002所有学科（手动展开，无i变量）
        *[(f'sc1111{j}', 's0011', 'ex001', f'c{str(1+j).zfill(4)}', min(100, 62+5*j), 8-j, '2025-04-10') for j in range(10)],
        *[(f'sc1121{j}', 's0011', 'ex002', f'c{str(1+j).zfill(4)}', min(100, 67+4*j), 8-j, '2025-06-20') for j in range(10)],
        *[(f'sc1211{j}', 's0012', 'ex001', f'c{str(1+j).zfill(4)}', min(100, 64+3*j), 8-j, '2025-04-10') for j in range(10)],
        *[(f'sc1221{j}', 's0012', 'ex002', f'c{str(1+j).zfill(4)}', min(100, 69+2*j), 8-j, '2025-06-20') for j in range(10)],
        *[(f'sc1311{j}', 's0013', 'ex001', f'c{str(1+j).zfill(4)}', min(100, 72+2*j), 8-j, '2025-04-10') for j in range(10)],
        *[(f'sc1321{j}', 's0013', 'ex002', f'c{str(1+j).zfill(4)}', min(100, 77+j), 8-j, '2025-06-20') for j in range(10)],
        *[(f'sc1411{j}', 's0014', 'ex001', f'c{str(1+j).zfill(4)}', min(100, 82+j), 8-j, '2025-04-10') for j in range(10)],
        *[(f'sc1421{j}', 's0014', 'ex002', f'c{str(1+j).zfill(4)}', min(100, 87+j), 8-j, '2025-06-20') for j in range(10)],
        *[(f'sc1511{j}', 's0015', 'ex001', f'c{str(1+j).zfill(4)}', min(100, 92-j), 8-j, '2025-04-10') for j in range(10)],
        *[(f'sc1521{j}', 's0015', 'ex002', f'c{str(1+j).zfill(4)}', min(100, 97-j), 8-j, '2025-06-20') for j in range(10)],
        *[(f'sc1611{j}', 's0016', 'ex001', f'c{str(1+j).zfill(4)}', min(100, 77+2*j), 8-j, '2025-04-10') for j in range(10)],
        *[(f'sc1621{j}', 's0016', 'ex002', f'c{str(1+j).zfill(4)}', min(100, 82+2*j), 8-j, '2025-06-20') for j in range(10)],
        *[(f'sc1711{j}', 's0017', 'ex001', f'c{str(1+j).zfill(4)}', min(100, 67+3*j), 8-j, '2025-04-10') for j in range(10)],
        *[(f'sc1721{j}', 's0017', 'ex002', f'c{str(1+j).zfill(4)}', min(100, 72+3*j), 8-j, '2025-06-20') for j in range(10)]
    ]
    for scid, sid, eid, subid, score, rank, cdate in scores:
        cursor.execute("INSERT INTO exam_score (score_id, student_id, exam_id, subject_id, score, ranking, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)", scid, sid, eid, subid, score, rank, cdate)

    # 8. 学习报告
    # s0001每次考试每科均有报告，日期与考试日期一致
    reports = []
    exam_teacher_map = {
        'ex001': [
            ('c0001', 't0001', '语文基础扎实，作文表达能力突出，需加强文言文阅读'),
            ('c0002', 't0002', '数学逻辑思维强，解题速度快，但需注意计算细节'),
            ('c0003', 't0003', '英语听说俱佳，阅读需加强'),
            ('c0004', 't0004', '物理基础扎实，实验能力突出'),
            ('c0005', 't0005', '化学反应原理掌握好，需多做题'),
            ('c0006', 't0006', '生物知识点掌握全面'),
            ('c0007', 't0007', '历史事件分析透彻'),
            ('c0008', 't0008', '地理图表判读能力强'),
            ('c0009', 't0009', '政治理论基础扎实'),
            ('c0010', 't0010', '体育积极参与，体能优秀')
        ],
        'ex002': [
            ('c0001', 't0001', '语文阅读能力提升明显'),
            ('c0002', 't0002', '数学计算细致，逻辑性强'),
            ('c0003', 't0003', '英语写作能力进步大'),
            ('c0004', 't0004', '物理题目分析能力增强'),
            ('c0005', 't0005', '化学实验操作规范'),
            ('c0006', 't0006', '生物实验设计有创新'),
            ('c0007', 't0007', '历史知识点记忆牢固'),
            ('c0008', 't0008', '地理区域认知能力提升'),
            ('c0009', 't0009', '政治时事关注度高'),
            ('c0010', 't0010', '体育成绩持续优秀')
        ],
        'ex003': [
            ('c0001', 't0001', '语文作文立意新颖'),
            ('c0002', 't0002', '数学思维活跃'),
            ('c0003', 't0003', '英语词汇量丰富'),
            ('c0004', 't0004', '物理公式运用熟练'),
            ('c0005', 't0005', '化学方程式书写规范'),
            ('c0006', 't0006', '生物实验观察细致'),
            ('c0007', 't0007', '历史材料分析能力强'),
            ('c0008', 't0008', '地理案例分析到位'),
            ('c0009', 't0009', '政治观点表达清晰'),
            ('c0010', 't0010', '体育锻炼积极主动')
        ],
        'ex004': [
            ('c0001', 't0001', '语文古诗文积累丰富'),
            ('c0002', 't0002', '数学解题速度提升'),
            ('c0003', 't0003', '英语语法掌握扎实'),
            ('c0004', 't0004', '物理实验探究能力强'),
            ('c0005', 't0005', '化学知识点掌握牢固'),
            ('c0006', 't0006', '生物遗传题表现优异'),
            ('c0007', 't0007', '历史答题条理清晰'),
            ('c0008', 't0008', '地理环境分析能力突出'),
            ('c0009', 't0009', '政治理论联系实际'),
            ('c0010', 't0010', '体育技能全面发展')
        ],
        'ex005': [
            ('c0001', 't0001', '语文表达能力持续进步'),
            ('c0002', 't0002', '数学综合运用能力强'),
            ('c0003', 't0003', '英语听力理解能力提升'),
            ('c0004', 't0004', '物理计算题准确率高'),
            ('c0005', 't0005', '化学实验题得分高'),
            ('c0006', 't0006', '生物知识迁移能力强'),
            ('c0007', 't0007', '历史大题分析有深度'),
            ('c0008', 't0008', '地理综合题表现优良'),
            ('c0009', 't0009', '政治论述条理清楚'),
            ('c0010', 't0010', '体育专项能力突出')
        ]
    }
    exam_dates = {
        'ex001': '2025-04-10',
        'ex002': '2025-06-20',
        'ex003': '2025-03-05',
        'ex004': '2025-05-08',
        'ex005': '2025-05-25',
    }
    report_id = 1000
    for eid, teacher_list in exam_teacher_map.items():
        for subid, tid, content in teacher_list:
            report_id += 1
            reports.append((f'rp{report_id}', 's0001', tid, exam_dates[eid], content, 'A'))
    for rid, sid, tid, rdate, content, level in reports:
        cursor.execute("INSERT INTO study_report (report_id, student_id, teacher_id, report_date, content, evaluation_level) VALUES (?, ?, ?, ?, ?, ?)", rid, sid, tid, rdate, content, level)

    # 9. 教师班级任课（每个老师都教三个班自己的主科）
    tcs = []
    for i in range(10):
        tid = f't{str(i+1).zfill(4)}'
        subid = f'c{str(i+1).zfill(4)}'
        for j, cid in enumerate(['cl001', 'cl002', 'cl003']):
            relid = f'r{str(i*3+j+1).zfill(4)}'
            tcs.append((relid, tid, cid, subid))
    for relid, tid, cid, subid in tcs:
        cursor.execute("INSERT INTO teacher_class_subject (relation_id, teacher_id, class_id, subject_id) VALUES (?, ?, ?, ?)", relid, tid, cid, subid)


    # 6. 排课表（每班一周全覆盖，且同一老师不会在不同班同一时段上课，每班课表不同）
    schedule_data = []
    all_class_ids = ['cl001', 'cl002', 'cl003']
    all_subjects = ['c0001', 'c0002', 'c0003', 'c0004', 'c0005', 'c0006', 'c0007', 'c0008', 'c0009', 'c0010']
    # 每个班级课表模板不同，主课优先，其他课补齐
    # 记录每个老师在每个时段是否已被占用
    teacher_busy = {}  # (week_day, period): set(teacher_id)
    # 学科-老师唯一映射
    subject_teacher_map = {
        'c0001': 't0001', 'c0002': 't0002', 'c0003': 't0003', 'c0004': 't0004', 'c0005': 't0005',
        'c0006': 't0006', 'c0007': 't0007', 'c0008': 't0008', 'c0009': 't0009', 'c0010': 't0010'
    }
    import random
    random.seed(42)
    for idx, class_id in enumerate(all_class_ids):
        # 每班课表顺序打乱，保证不同
        subjects_order = all_subjects[:]
        random.shuffle(subjects_order)
        for week_day in range(1, 6):  # 周一到周五
            for period in range(1, 9):  # 1-8节
                # 循环分配学科，保证每班课表不同
                sub_idx = ((week_day-1)*8+period-1+idx*3) % len(subjects_order)
                subject_id = subjects_order[sub_idx]
                teacher_id = subject_teacher_map[subject_id]
                # 检查老师是否在该时段已被其它班占用
                busy_key = (week_day, period)
                if busy_key not in teacher_busy:
                    teacher_busy[busy_key] = set()
                # 若冲突，换下一个可用学科（老师）
                orig_subject_id = subject_id
                orig_teacher_id = teacher_id
                tried = set()
                while teacher_id in teacher_busy[busy_key]:
                    tried.add(subject_id)
                    # 找下一个没被占用的学科
                    found = False
                    for sid in subjects_order:
                        if sid not in tried and subject_teacher_map[sid] not in teacher_busy[busy_key]:
                            subject_id = sid
                            teacher_id = subject_teacher_map[subject_id]
                            found = True
                            break
                    if not found:
                        # 所有老师都被占用，留空
                        subject_id = None
                        teacher_id = None
                        break
                if teacher_id:
                    teacher_busy[busy_key].add(teacher_id)
                classroom = f'{class_id.upper()}教室'
                remark = ''
                schedule_data.append((class_id, week_day, period, subject_id, teacher_id, classroom, remark))
    for class_id, week_day, period, subject_id, teacher_id, classroom, remark in schedule_data:
        cursor.execute("""
            INSERT INTO schedule (class_id, week_day, period, subject_id, teacher_id, classroom, remark)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, class_id, week_day, period, subject_id, teacher_id, classroom, remark)

    # 10. 班级成绩分析报告
    class_exam_reports = [
        ('cr001', 't0001', 'cl001', 'ex001', '高一(1)班2025期中考试整体表现良好，语文平均分85，数学突出，需加强英语学习。'),
        ('cr002', 't0001', 'cl001', 'ex002', '高一(1)班2025期末考试整体进步明显，数学和物理成绩提升较大。'),
        ('cr003', 't0002', 'cl002', 'ex001', '高一(2)班2025期中考试整体成绩中等，部分学生需加强基础知识。'),
        ('cr004', 't0003', 'cl003', 'ex003', '高二(1)班2025年3月月考理科成绩优秀，文科需提升。'),
        # 新增数据
        ('cr005', 't0002', 'cl002', 'ex002', '高一(2)班2025期末考试整体进步，数学平均分提升，英语仍需努力。'),
        ('cr006', 't0003', 'cl003', 'ex004', '高二(1)班2025年5月月考班级整体稳定，部分学生成绩波动较大。'),
        ('cr007', 't0001', 'cl001', 'ex003', '高一(1)班2025年3月月考语文成绩优秀，需关注理科短板。'),
        ('cr008', 't0004', 'cl002', 'ex001', '高一(2)班物理成绩整体良好，实验题得分高。')
    ]
    for rid, tid, cid, eid, content in class_exam_reports:
        cursor.execute("""
            INSERT INTO class_exam_report (report_id, teacher_id, class_id, exam_id, content)
            VALUES (?, ?, ?, ?, ?)
        """, rid, tid, cid, eid, content)
    conn.commit()
    cursor.close()
    conn.close()
    print('测试数据插入完成！')





#123

# ——推送/评论相关数据库操作示例——
def insert_class_push(classmaster_name, title, content, push_type, is_top=0, top_days=0, attachment_url=None):
    """
    插入一条推送数据到 class_push 表。
    :param classmaster_name: 班主任姓名
    :param title: 推送标题
    :param content: 推送内容
    :param push_type: 推送类型
    :param is_top: 是否置顶（0/1）
    :param top_days: 置顶天数
    :param attachment_url: 附件路径
    """
    conn = get_conn()
    cursor = conn.cursor()
    # 获取班主任id和班级id
    cursor.execute('SELECT teacher_id FROM teacher WHERE name=?', classmaster_name)
    row = cursor.fetchone()
    if not row:
        conn.close()
        print('班主任不存在')
        return
    teacher_id = row[0]
    cursor.execute('SELECT class_id FROM class WHERE head_teacher_id=?', teacher_id)
    row = cursor.fetchone()
    if not row:
        conn.close()
        print('未找到班级')
        return
    class_id = row[0]
    import uuid
    push_id = str(uuid.uuid4())[:20]
    from datetime import datetime, timedelta
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    top_expire = (datetime.now() + timedelta(days=top_days)).strftime('%Y-%m-%d %H:%M:%S') if is_top and top_days else None
    # 插入推送表
    cursor.execute('''
        INSERT INTO class_push (push_id, class_id, publisher_id, publisher_role, title, content, push_type, is_top, top_expire, attachment_path, create_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (push_id, class_id, teacher_id, 'classmaster', title, content, push_type, is_top, top_expire, attachment_url, now))
    conn.commit()
    conn.close()
    print('推送已插入')

def fetch_class_push_list(class_id=None, push_type=None):
    """
    查询推送列表，可按班级和类型筛选。
    :param class_id: 班级ID
    :param push_type: 推送类型
    :return: 推送记录列表
    """
    conn = get_conn()
    cursor = conn.cursor()
    sql = 'SELECT push_id, title, content, push_type, is_top, top_expire, attachment_path, publisher_id, publisher_role, create_time FROM class_push WHERE 1=1'
    params = []
    if class_id:
        sql += ' AND class_id=?'
        params.append(class_id)
    if push_type:
        sql += ' AND push_type=?'
        params.append(push_type)
    sql += ' ORDER BY is_top DESC, (CASE WHEN top_expire IS NOT NULL AND top_expire>GETDATE() THEN 1 ELSE 0 END) DESC, create_time DESC'
    cursor.execute(sql, *params)
    rows = cursor.fetchall()
    conn.close()
    return rows




if __name__ == '__main__':
    insert_test_data()




