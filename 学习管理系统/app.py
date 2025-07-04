from flask import Flask, render_template, request, redirect, url_for, flash, session
import pyodbc
from flask import jsonify

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', '').strip()
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        conn = get_conn()
        cursor = conn.cursor()
        # 用户名唯一校验
        cursor.execute("SELECT 1 FROM [user] WHERE username=?", username)
        if cursor.fetchone():
            flash('用户名已存在', 'danger')
            conn.close()
            return redirect(url_for('register'))
        # 角色分支
        if role == 'student':
            student_id = request.form.get('student_id', '').strip()
            gender = request.form.get('gender', '').strip()
            birth_date = request.form.get('birth_date', '').strip()
            nation = request.form.get('nation', '').strip()
            province = request.form.get('province', '').strip()
            political_status = request.form.get('political_status', '').strip()
            class_id = request.form.get('class_id', '').strip()
            contact_phone = request.form.get('contact_phone', '').strip()
            emergency_contact = request.form.get('emergency_contact', '').strip()
            # 学号唯一校验
            cursor.execute('SELECT 1 FROM student WHERE student_id=?', student_id)
            if cursor.fetchone():
                flash('学号已存在', 'danger')
                conn.close()
                return redirect(url_for('register'))
            # 插入user表（user_id=student_id）
            cursor.execute("INSERT INTO [user] (user_id, username, password, role, name, created_at) VALUES (?, ?, ?, ?, ?, GETDATE())", username, student_id, password, role, name)
            # 插入student表
            cursor.execute('''INSERT INTO student (student_id, name, gender, birth_date, nation, province, political_status, class_id, contact_phone, emergency_contact, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())''',
                student_id, name, gender, birth_date, nation, province, political_status, class_id, contact_phone, emergency_contact)
            conn.commit()
            conn.close()
            flash('学生注册成功，请登录', 'success')
            return redirect(url_for('login'))
        elif role == 'teacher':
            teacher_id = request.form.get('teacher_id', '').strip()
            gender = request.form.get('gender', '').strip()
            title = request.form.get('title', '').strip()
            subject_id = request.form.get('subject_id', '').strip()
            contact_email = request.form.get('contact_email', '').strip()
            office_address = request.form.get('office_address', '').strip()
            phone = request.form.get('phone', '').strip()
            # 工号唯一校验
            cursor.execute('SELECT 1 FROM teacher WHERE teacher_id=?', teacher_id)
            if cursor.fetchone():
                flash('工号已存在', 'danger')
                conn.close()
                return redirect(url_for('register'))
            # 插入user表（user_id=teacher_id）
            cursor.execute("INSERT INTO [user] (user_id, username, password, role, name, created_at) VALUES (?, ?, ?, ?, ?, GETDATE())", teacher_id, username, password, role, name)
            # 插入teacher表
            cursor.execute('''INSERT INTO teacher (teacher_id, name, gender, title, subject_id, contact_email, office_address, phone, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE())''',
                teacher_id, name, gender, title, subject_id, contact_email, office_address, phone)
            conn.commit()
            conn.close()
            flash('老师注册成功，请登录', 'success')
            return redirect(url_for('login'))
        elif role == 'classmaster':
            teacher_id = request.form.get('teacher_id', '').strip()
            gender = request.form.get('gender', '').strip()
            title = request.form.get('title', '').strip()
            contact_email = request.form.get('contact_email', '').strip()
            office_address = request.form.get('office_address', '').strip()
            phone = request.form.get('phone', '').strip()
            class_id = request.form.get('class_id', '').strip()
            grade_level = request.form.get('grade_level', '').strip()
            # 工号唯一校验
            cursor.execute('SELECT 1 FROM teacher WHERE teacher_id=?', teacher_id)
            if cursor.fetchone():
                flash('工号已存在', 'danger')
                conn.close()
                return redirect(url_for('register'))
            # 班级ID唯一校验
            cursor.execute('SELECT 1 FROM class WHERE class_id=?', class_id)
            if cursor.fetchone():
                flash('班级ID已存在', 'danger')
                conn.close()
                return redirect(url_for('register'))
            # 插入user表（user_id=teacher_id）
            cursor.execute("INSERT INTO [user] (user_id, username, password, role, name, created_at) VALUES (?, ?, ?, ?, ?, GETDATE())", teacher_id, username, password, role, name)
            # 插入teacher表（is_head_teacher=1）
            cursor.execute('''INSERT INTO teacher (teacher_id, name, gender, title, contact_email, office_address, phone, is_head_teacher, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, 1, GETDATE())''',
                teacher_id, name, gender, title, contact_email, office_address, phone)
            # 插入class表
            cursor.execute('''INSERT INTO class (class_id, class_name, head_teacher_id, grade_level) VALUES (?, ?, ?, ?)''',
                class_id, class_id, teacher_id, grade_level)
            conn.commit()
            conn.close()
            flash('班主任注册成功，请登录', 'success')
            return redirect(url_for('login'))
        else:
            conn.close()
            flash('请选择正确的身份', 'danger')
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, username, role, name FROM [user] WHERE username=? AND password=?", username, password)
        user = cursor.fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[2]
            session['name'] = user[3]
            if user[2] == 'student':
                return redirect(url_for('student_profile'))
            elif user[2] == 'teacher':
                return redirect(url_for('teacher_profile'))
            elif user[2] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user[2] == 'classmaster':
                return redirect(url_for('classmaster_profile'))
        else:
            flash('用户名或密码错误', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# 管理员-控制面板
@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    conn = get_conn()
    cursor = conn.cursor()
    # 统计各类用户数量
    cursor.execute("SELECT COUNT(*) FROM student")
    student_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM teacher")
    teacher_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM class")
    class_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM subject")
    course_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM [user] WHERE role='admin'")
    admin_count = cursor.fetchone()[0]
    # 查询管理员详细信息
    admin_user_id = session.get('username')
    cursor.execute("SELECT cno, cname FROM administrator WHERE cno=?", admin_user_id)
    admin_row = cursor.fetchone()
    if admin_row:
        admin_info = {'cno': admin_row[0], 'cname': admin_row[1]}
    else:
        admin_info = {'cno': admin_user_id, 'cname': session.get('name')}
    conn.close()
    return render_template('admin/dashboard.html',
                           admin=admin_info,
                           student_count=student_count,
                           teacher_count=teacher_count,
                           class_count=class_count,
                           course_count=course_count,
                           admin_count=admin_count)

# 管理员-用户管理
@app.route('/admin/manage_users')
def admin_manage_users():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    conn = get_conn()
    cursor = conn.cursor()
    # 查询所有学生
    cursor.execute('''
        SELECT s.student_id, s.name, s.gender, c.class_name, s.contact_phone
        FROM student s
        LEFT JOIN class c ON s.class_id = c.class_id
        ORDER BY s.student_id
    ''')
    students = [
        {
            'student_id': row[0],
            'name': row[1],
            'gender': row[2],
            'class_name': row[3] or '',
            'contact_phone': row[4] or ''
        } for row in cursor.fetchall()
    ]
    # 查询所有教师
    cursor.execute('''
        SELECT teacher_id, name, gender, title, contact_email, phone
        FROM teacher
        ORDER BY teacher_id
    ''')
    teachers = [
        {
            'teacher_id': row[0],
            'name': row[1],
            'gender': row[2],
            'title': row[3] or '',
            'contact_email': row[4] or '',
            'phone': row[5] or ''
        } for row in cursor.fetchall()
    ]
    # 查询所有管理员
    cursor.execute('SELECT cno, cname FROM administrator ORDER BY cno')
    admins = [
        {'cno': row[0], 'cname': row[1]} for row in cursor.fetchall()
    ]
    conn.close()
    return render_template('admin/manage_users.html', students=students, teachers=teachers, admins=admins)

# 管理员-用户详情
@app.route('/admin/view_user/<user_type>/<user_id>')
def admin_view_user(user_type, user_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    conn = get_conn()
    cursor = conn.cursor()
    user = None
    if user_type == 'student':
        cursor.execute('''
            SELECT s.student_id, s.name, s.gender, s.birth_date, s.nation, s.province, s.political_status, c.class_name, s.contact_phone, s.emergency_contact
            FROM student s
            LEFT JOIN class c ON s.class_id = c.class_id
            WHERE s.student_id = ?
        ''', user_id)
        row = cursor.fetchone()
        if row:
            user = {
                'student_id': row[0], 'name': row[1], 'gender': row[2], 'birth_date': row[3], 'nation': row[4],
                'province': row[5], 'political_status': row[6], 'class_name': row[7], 'contact_phone': row[8], 'emergency_contact': row[9]
            }
    elif user_type == 'teacher':
        cursor.execute('''
            SELECT teacher_id, name, gender, title, contact_email, office_address, phone
            FROM teacher WHERE teacher_id = ?
        ''', user_id)
        row = cursor.fetchone()
        if row:
            user = {
                'teacher_id': row[0], 'name': row[1], 'gender': row[2], 'title': row[3],
                'contact_email': row[4], 'office_address': row[5], 'phone': row[6]
            }
    elif user_type == 'admin':
        cursor.execute('SELECT cno, cname FROM administrator WHERE cno=?', user_id)
        row = cursor.fetchone()
        if row:
            user = {'cno': row[0], 'cname': row[1]}
    conn.close()
    return render_template('admin/view_user.html', user=user, user_type=user_type)

# 管理员-用户编辑
@app.route('/admin/edit_user/<user_type>/<user_id>', methods=['GET', 'POST'])
def admin_edit_user(user_type, user_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    conn = get_conn()
    cursor = conn.cursor()
    if request.method == 'POST':
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        password_error = None
        if new_password:
            if len(new_password) < 4 or len(new_password) > 32:
                password_error = '密码长度需为4-32位'
            elif new_password != confirm_password:
                password_error = '两次输入的密码不一致'
        if user_type == 'student':
            name = request.form.get('name')
            gender = request.form.get('gender')
            contact_phone = request.form.get('contact_phone')
            cursor.execute('UPDATE student SET name=?, gender=?, contact_phone=? WHERE student_id=?', name, gender, contact_phone, user_id)
        elif user_type == 'teacher':
            name = request.form.get('name')
            title = request.form.get('title')
            phone = request.form.get('phone')
            cursor.execute('UPDATE teacher SET name=?, title=?, phone=? WHERE teacher_id=?', name, title, phone, user_id)
        elif user_type == 'admin':
            cname = request.form.get('cname')
            cursor.execute('UPDATE administrator SET cname=? WHERE cno=?', cname, user_id)
        # 密码校验通过才更新密码
        if new_password:
            if password_error:
                conn.close()
                flash(password_error, 'danger')
                return redirect(request.url)
            # user表的username与三类主键一致
            username = user_id
            cursor.execute('UPDATE [user] SET password=? WHERE username=?', new_password, username)
        conn.commit()
        conn.close()
        flash('信息已更新', 'success')
        return redirect(url_for('admin_manage_users'))
    # GET请求，查原始数据
    user = None
    if user_type == 'student':
        cursor.execute('SELECT student_id, name, gender, contact_phone FROM student WHERE student_id=?', user_id)
        row = cursor.fetchone()
        if row:
            user = {'student_id': row[0], 'name': row[1], 'gender': row[2], 'contact_phone': row[3]}
    elif user_type == 'teacher':
        cursor.execute('SELECT teacher_id, name, title, phone FROM teacher WHERE teacher_id=?', user_id)
        row = cursor.fetchone()
        if row:
            user = {'teacher_id': row[0], 'name': row[1], 'title': row[2], 'phone': row[3]}
    elif user_type == 'admin':
        cursor.execute('SELECT cno, cname FROM administrator WHERE cno=?', user_id)
        row = cursor.fetchone()
        if row:
            user = {'cno': row[0], 'cname': row[1]}
    conn.close()
    return render_template('admin/edit_user.html', user_type=user_type, user_id=user_id, user=user)

# 管理员-用户删除
@app.route('/admin/delete_user/<user_type>/<user_id>', methods=['GET', 'POST'])
def admin_delete_user(user_type, user_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    if request.method == 'POST':
        conn = get_conn()
        cursor = conn.cursor()
        if user_type == 'student':
            cursor.execute('DELETE FROM student WHERE student_id=?', user_id)
            cursor.execute('DELETE FROM [user] WHERE username=?', user_id)
        elif user_type == 'teacher':
            cursor.execute('DELETE FROM teacher WHERE teacher_id=?', user_id)
            cursor.execute('DELETE FROM [user] WHERE username=?', user_id)
        elif user_type == 'admin':
            cursor.execute('DELETE FROM administrator WHERE cno=?', user_id)
            cursor.execute('DELETE FROM [user] WHERE username=?', user_id)
        conn.commit()
        conn.close()
        flash('用户已删除', 'success')
        return redirect(url_for('admin_manage_users'))
    return render_template('admin/delete_user.html', user_type=user_type, user_id=user_id)

# 管理员-重置用户密码


@app.route('/admin/reset_password/<user_type>/<user_id>', methods=['POST'])
def admin_reset_password(user_type, user_id):
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'msg': '无权限'}), 403
    data = request.get_json()
    new_password = data.get('new_password', '').strip()
    if not new_password or len(new_password) < 4 or len(new_password) > 32:
        return jsonify({'success': False, 'msg': '密码长度需为4-32位'}), 400
    conn = get_conn()
    cursor = conn.cursor()
    # 用户表 user_id 字段和三类用户的主键映射
    username = None
    if user_type == 'student':
        username = user_id
    elif user_type == 'teacher':
        username = user_id
    elif user_type == 'admin':
        username = user_id
    else:
        conn.close()
        return jsonify({'success': False, 'msg': '用户类型错误'}), 400
    cursor.execute('UPDATE [user] SET password=? WHERE username=?', new_password, username)
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'success': False, 'msg': '未找到该用户'}), 404
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# ================== 课程排课管理相关接口 ==================
# 1. 获取所有班级列表
@app.route('/admin/schedule/classes')
def admin_schedule_classes():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'msg': '无权限'}), 403
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('SELECT class_id, class_name FROM class ORDER BY class_id')
    classes = [{'class_id': row[0], 'class_name': row[1]} for row in cursor.fetchall()]
    conn.close()
    return jsonify({'success': True, 'classes': classes})


# 管理员-查看课表页面（与教师端一致，只读，可切换班级）
@app.route('/admin/schedule_page', methods=['GET'])
def admin_schedule_page():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    conn = get_conn()
    cursor = conn.cursor()
    # 获取所有班级
    cursor.execute('SELECT class_id, class_name FROM class ORDER BY class_id')
    classes = [{'class_id': r[0], 'class_name': r[1]} for r in cursor.fetchall()]
    # 当前选中班级
    current_class_id = request.args.get('class_id') or (classes[0]['class_id'] if classes else None)
    # 获取所有课程和教师
    cursor.execute('SELECT subject_id, subject_name FROM subject ORDER BY subject_id')
    subjects = [{'subject_id': r[0], 'subject_name': r[1]} for r in cursor.fetchall()]
    cursor.execute('SELECT teacher_id, name FROM teacher ORDER BY teacher_id')
    teachers = [{'teacher_id': r[0], 'name': r[1]} for r in cursor.fetchall()]
    # 查询当前班级课表
    schedule_map = {}
    if current_class_id:
        cursor.execute('SELECT week_day, period, subject_id, teacher_id FROM schedule WHERE class_id=?', current_class_id)
        for r in cursor.fetchall():
            schedule_map[(r[0], r[1])] = {'subject_id': r[2], 'teacher_id': r[3]}
    conn.close()
    weekdays = ['一','二','三','四','五','六','日']
    periods = list(range(1,9))
    return render_template('admin/schedule.html', schedule_map=schedule_map, classes=classes, current_class_id=current_class_id, subjects=subjects, teachers=teachers, weekdays=weekdays, periods=periods)

# 2. 获取指定班级课表
@app.route('/admin/schedule')
def admin_schedule():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'msg': '无权限'}), 403
    class_id = request.args.get('class_id')
    if not class_id:
        return jsonify({'success': False, 'msg': '缺少class_id'}), 400
    conn = get_conn()
    cursor = conn.cursor()
    # 查询课表，按week_day, period排序
    cursor.execute('''
        SELECT schedule_id, week_day, period, subject_id, teacher_id
        FROM schedule
        WHERE class_id = ?
        ORDER BY week_day, period
    ''', class_id)
    schedule_rows = cursor.fetchall()
    # 查询所有课程和教师，便于前端下拉选择
    cursor.execute('SELECT subject_id, subject_name FROM subject ORDER BY subject_id')
    subjects = [{'subject_id': row[0], 'subject_name': row[1]} for row in cursor.fetchall()]
    cursor.execute('SELECT teacher_id, name FROM teacher ORDER BY teacher_id')
    teachers = [{'teacher_id': row[0], 'name': row[1]} for row in cursor.fetchall()]
    conn.close()
    # 组装课表数据
    schedule = [
        {
            'schedule_id': row[0],
            'week_day': row[1],
            'period': row[2],
            'subject_id': row[3],
            'teacher_id': row[4]
        } for row in schedule_rows
    ]
    return jsonify({'success': True, 'schedule': schedule, 'subjects': subjects, 'teachers': teachers})

# 3. 保存/更新班级课表
@app.route('/admin/schedule/save', methods=['POST'])
def admin_schedule_save():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'msg': '无权限'}), 403
    data = request.get_json()
    class_id = data.get('class_id')
    schedule_data = data.get('schedule')  # list of {week_day, period, subject_id, teacher_id}
    if not class_id or not isinstance(schedule_data, list):
        return jsonify({'success': False, 'msg': '参数错误'}), 400
    conn = get_conn()
    cursor = conn.cursor()
    # 先删除该班级原有课表
    cursor.execute('DELETE FROM schedule WHERE class_id=?', class_id)
    # 批量插入新课表
    for item in schedule_data:
        week_day = item.get('week_day')
        period = item.get('period')
        subject_id = item.get('subject_id')
        teacher_id = item.get('teacher_id')
        if not (week_day and period and subject_id and teacher_id):
            continue
        cursor.execute('''
            INSERT INTO schedule (class_id, week_day, period, subject_id, teacher_id)
            VALUES (?, ?, ?, ?, ?)
        ''', class_id, week_day, period, subject_id, teacher_id)
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'msg': '课表已保存'})

# 学生模块
@app.route('/student/profile')
def student_profile():
    if session.get('role') != 'student':
        return redirect(url_for('login'))
    student_id = session.get('user_id')
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM [user] WHERE user_id=?', student_id)
    stu_username = cursor.fetchone()
    if not stu_username:
        conn.close()
        return render_template('student/profile.html', info={})
    student_id = stu_username[0]
    cursor.execute('''
        SELECT s.student_id, s.name, s.gender, s.birth_date, s.nation, s.province, s.political_status, c.class_name, s.contact_phone, s.emergency_contact
        FROM student s
        JOIN class c ON s.class_id = c.class_id
        WHERE s.student_id = ?
    ''', student_id)
    row = cursor.fetchone()
    conn.close()
    info = {
        'student_id': row[0],
        'name': row[1],
        'gender': row[2],
        'birth_date': row[3],
        'nation': row[4],
        'province': row[5],
        'political_status': row[6],
        'class_name': row[7],
        'contact_phone': row[8],
        'emergency_contact': row[9]
    } if row else {}
    return render_template('student/profile.html', info=info)


# 学生-查看班级课表
@app.route('/student/schedule')
def student_schedule():
    if session.get('role') != 'student':
        return redirect(url_for('login'))
    student_id = session.get('username')
    conn = get_conn()
    cursor = conn.cursor()
    # 查找学生所在班级
    cursor.execute('SELECT class_id FROM student WHERE student_id=?', student_id)
    row = cursor.fetchone()
    if not row or not row[0]:
        conn.close()
        return render_template('student/schedule.html', schedule_map={}, subjects=[], teachers=[], weekdays=['一','二','三','四','五','六','日'], periods=list(range(1,9)))
    class_id = row[0]
    # 获取所有课程和教师
    cursor.execute('SELECT subject_id, subject_name FROM subject ORDER BY subject_id')
    subjects = [{'subject_id': r[0], 'subject_name': r[1]} for r in cursor.fetchall()]
    cursor.execute('SELECT teacher_id, name FROM teacher ORDER BY teacher_id')
    teachers = [{'teacher_id': r[0], 'name': r[1]} for r in cursor.fetchall()]
    # 查询本班课表
    schedule_map = {}
    cursor.execute('SELECT week_day, period, subject_id, teacher_id FROM schedule WHERE class_id=?', class_id)
    for r in cursor.fetchall():
        schedule_map[(r[0], r[1])] = {'subject_id': r[2], 'teacher_id': r[3]}
    conn.close()
    weekdays = ['一','二','三','四','五','六','日']
    periods = list(range(1,9))
    return render_template('student/schedule.html', schedule_map=schedule_map, subjects=subjects, teachers=teachers, weekdays=weekdays, periods=periods)




@app.route('/student/profile/edit', methods=['POST'])
def student_profile_edit():
    if session.get('role') != 'student':
        return redirect(url_for('login'))
    student_id = session.get('user_id')
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM [user] WHERE user_id=?', student_id)
    stu_username = cursor.fetchone()
    if not stu_username:
        conn.close()
        flash('未找到学生信息', 'danger')
        return redirect(url_for('student_profile'))
    student_id = stu_username[0]
    name = request.form['name']
    gender = request.form['gender']
    birth_date = request.form['birth_date']
    nation = request.form['nation']
    province = request.form['province']
    political_status = request.form['political_status']
    contact_phone = request.form['contact_phone']
    emergency_contact = request.form['emergency_contact']
    cursor.execute('''
        UPDATE student SET name=?, gender=?, birth_date=?, nation=?, province=?, political_status=?, contact_phone=?, emergency_contact=? WHERE student_id=?
    ''', name, gender, birth_date, nation, province, political_status, contact_phone, emergency_contact, student_id)
    conn.commit()
    conn.close()
    flash('个人档案已更新', 'success')
    return redirect(url_for('student_profile'))

@app.route('/student/score')
def student_score():
    if session.get('role') != 'student':
        return redirect(url_for('login'))
    student_id = session.get('username')
    kw = request.args.get('kw', '').strip()
    conn = get_conn()
    cursor = conn.cursor()
    # 1. 查找本学生所在班级
    cursor.execute('SELECT class_id FROM student WHERE student_id=?', student_id)
    class_row = cursor.fetchone()
    class_id = class_row[0] if class_row else None
    # 2. 查询所有考试-学科成绩
    sql = '''
        SELECT e.exam_id, e.exam_name, e.exam_type, e.exam_date, s.subject_id, s.subject_name, es.score
        FROM exam_score es
        JOIN exam e ON es.exam_id = e.exam_id
        JOIN subject s ON es.subject_id = s.subject_id
        WHERE es.student_id = ?
    '''
    params = [student_id]
    if kw:
        sql += " AND e.exam_name LIKE ?"
        params.append(f'%{kw}%')
    sql += " ORDER BY e.exam_date DESC, s.subject_id"
    cursor.execute(sql, *params)
    rows = cursor.fetchall()
    # 3. 按考试分组，准备每场考试的各科成绩
    from collections import defaultdict
    exams = defaultdict(list)
    exam_ids = set()
    for r in rows:
        exam_id = r[0]
        exam_ids.add(exam_id)
        # 强制将成绩转为 float，无法转则为0
        try:
            score_val = float(r[6]) if r[6] is not None and r[6] != '' else 0
        except Exception:
            score_val = 0
        exams[(r[1], r[2], r[3], exam_id)].append({
            'subject_id': r[4],
            'subject': r[5],
            'score': score_val
        })
    # 4. 查询每场考试所有学生的总分，计算班级/学校排名
    exam_total_info = {}  # exam_id -> {student_id: total, ...}
    exam_class_total = {} # exam_id -> {student_id: total, ...} 仅本班
    for eid in exam_ids:
        # 全校总分
        cursor.execute('''
            SELECT es.student_id, SUM(es.score) as total
            FROM exam_score es
            WHERE es.exam_id=?
            GROUP BY es.student_id
        ''', eid)
        exam_total_info[eid] = {row[0]: float(row[1]) for row in cursor.fetchall()}
        # 本班总分
        if class_id:
            cursor.execute('''
                SELECT es.student_id, SUM(es.score) as total
                FROM exam_score es
                JOIN student st ON es.student_id = st.student_id
                WHERE es.exam_id=? AND st.class_id=?
                GROUP BY es.student_id
            ''', eid, class_id)
            exam_class_total[eid] = {row[0]: float(row[1]) for row in cursor.fetchall()}
        else:
            exam_class_total[eid] = {}
    # 5. 查询每场考试所有学生各科成绩，计算班级/学校排名
    subject_rank_info = {}  # (exam_id, subject_id) -> [(student_id, score), ...]
    subject_class_rank = {} # (exam_id, subject_id) -> [(student_id, score), ...] 仅本班
    for eid in exam_ids:
        cursor.execute('''
            SELECT es.student_id, es.subject_id, es.score
            FROM exam_score es
            WHERE es.exam_id=?
        ''', eid)
        for row in cursor.fetchall():
            key = (eid, row[1])
            subject_rank_info.setdefault(key, []).append((row[0], float(row[2]) if row[2] is not None else 0))
        if class_id:
            cursor.execute('''
                SELECT es.student_id, es.subject_id, es.score
                FROM exam_score es
                JOIN student st ON es.student_id = st.student_id
                WHERE es.exam_id=? AND st.class_id=?
            ''', eid, class_id)
            for row in cursor.fetchall():
                key = (eid, row[1])
                subject_class_rank.setdefault(key, []).append((row[0], float(row[2]) if row[2] is not None else 0))
    # 6. 组装前端数据
    exam_list = []
    for (exam_name, exam_type, exam_date, exam_id), score_list in exams.items():
        # 计算总分
        total_score = sum(s['score'] for s in score_list if isinstance(s['score'], (int, float)))
        # 总分排名及总人数
        school_total_list = sorted(exam_total_info.get(exam_id, {}).items(), key=lambda x: -x[1])
        class_total_list = sorted(exam_class_total.get(exam_id, {}).items(), key=lambda x: -x[1])
        school_total_rank = next((i+1 for i, (sid, _) in enumerate(school_total_list) if sid == student_id), None)
        class_total_rank = next((i+1 for i, (sid, _) in enumerate(class_total_list) if sid == student_id), None)
        school_total_count = len(school_total_list)
        class_total_count = len(class_total_list)
        # 每科成绩补充排名
        scores = []
        for s in score_list:
            key = (exam_id, s['subject_id'])
            # 学校排名
            school_list = sorted(subject_rank_info.get(key, []), key=lambda x: -x[1])
            school_ranking = next((i+1 for i, (sid, _) in enumerate(school_list) if sid == student_id), None)
            school_count = len(school_list)
            # 班级排名
            class_list = sorted(subject_class_rank.get(key, []), key=lambda x: -x[1])
            class_ranking = next((i+1 for i, (sid, _) in enumerate(class_list) if sid == student_id), None)
            class_count = len(class_list)
            scores.append({
                'subject': s['subject'],
                'score': s['score'],
                'class_ranking': f"{class_ranking}/{class_count}" if class_ranking else '-',
                'school_ranking': f"{school_ranking}/{school_count}" if school_ranking else '-'
            })
        # 总分行也补充排名
        exam_list.append({
            'exam_name': exam_name,
            'exam_type': exam_type,
            'exam_date': exam_date,
            'scores': scores,
            'total_score': total_score,
            'total_class_ranking': f"{class_total_rank}/{class_total_count}" if class_total_rank else '-',
            'total_school_ranking': f"{school_total_rank}/{school_total_count}" if school_total_rank else '-'
        })
    conn.close()
    return render_template('student/score.html', exam_list=exam_list, kw=kw)

@app.route('/student/analysis')
def student_analysis():
    if session.get('role') != 'student':
        return redirect(url_for('login'))
    student_id = session.get('username')
    conn = get_conn()
    cursor = conn.cursor()
    # 查询所有考试，按时间升序
    cursor.execute('''
        SELECT e.exam_id, e.exam_name, e.exam_date
        FROM exam_score es
        JOIN exam e ON es.exam_id = e.exam_id
        WHERE es.student_id = ?
        GROUP BY e.exam_id, e.exam_name, e.exam_date
        ORDER BY e.exam_date ASC
    ''', student_id)
    exams = cursor.fetchall()
    exam_labels = [f"{row[1]}({row[2]})" for row in exams] if exams else []
    exam_ids = [row[0] for row in exams] if exams else []
    # 查询所有学科
    cursor.execute('''
        SELECT DISTINCT s.subject_id, s.subject_name
        FROM exam_score es
        JOIN subject s ON es.subject_id = s.subject_id
        WHERE es.student_id = ?
        ORDER BY s.subject_id
    ''', student_id)
    subjects = cursor.fetchall()
    chart_data = []
    for sub in subjects:
        subid, subname = sub
        scores = []
        for eid in exam_ids:
            cursor.execute('''
                SELECT score FROM exam_score WHERE student_id=? AND exam_id=? AND subject_id=?
            ''', student_id, eid, subid)
            r = cursor.fetchone()
            scores.append(r[0] if r else None)
        chart_data.append({'subject_id': subid, 'subject_name': subname, 'scores': scores})
    conn.close()
    return render_template('student/analysis.html', exam_labels=exam_labels, chart_data=chart_data)

@app.route('/student/report')
def student_report():
    if session.get('role') != 'student':
        return redirect(url_for('login'))
    student_id = session.get('username')
    exam_id = request.args.get('exam_id')
    conn = get_conn()
    cursor = conn.cursor()
    # 查询所有考试（按时间降序）
    cursor.execute('''
        SELECT DISTINCT e.exam_id, e.exam_name, e.exam_date
        FROM exam_score es
        JOIN exam e ON es.exam_id = e.exam_id
        WHERE es.student_id = ?
        ORDER BY e.exam_date DESC
    ''', student_id)
    exams = cursor.fetchall()
    exam_list = [
        {'exam_id': row[0], 'exam_name': row[1], 'exam_date': str(row[2])}
        for row in exams
    ]
    # 默认选中最新一次考试
    if not exam_id and exam_list:
        exam_id = str(exam_list[0]['exam_id'])
    # 查询该考试下所有学科及成绩
    subjects, scores, reports = [], [], []
    if exam_id:
        # 先查考试日期
        cursor.execute('SELECT exam_date FROM exam WHERE exam_id=?', exam_id)
        exam_date_row = cursor.fetchone()
        if exam_date_row:
            from datetime import datetime, timedelta
            exam_date = exam_date_row[0]
            if isinstance(exam_date, str):
                exam_date = datetime.strptime(exam_date, '%Y-%m-%d')
            date_start = (exam_date - timedelta(days=3)).strftime('%Y-%m-%d')
            date_end = (exam_date + timedelta(days=3)).strftime('%Y-%m-%d')
        else:
            date_start = date_end = None

        # 查询所有学科、成绩、教师id、教师姓名
        cursor.execute('''
            SELECT s.subject_id, s.subject_name, es.score, t.teacher_id, t.name
            FROM exam_score es
            JOIN subject s ON es.subject_id = s.subject_id
            LEFT JOIN teacher t ON t.subject_id = s.subject_id
            WHERE es.student_id = ? AND es.exam_id = ?
            ORDER BY s.subject_id
        ''', student_id, exam_id)
        rows = cursor.fetchall()

        # 查询本学生在本考试前后3天内所有老师的报告，放入字典
        report_dict = {}
        if date_start and date_end:
            cursor.execute('''
                SELECT teacher_id, content FROM study_report WHERE student_id=? AND report_date>=? AND report_date<=?
            ''', student_id, date_start, date_end)
            for tid, content in cursor.fetchall():
                report_dict[tid] = content

        for row in rows:
            subid, subname, score, tid, tname = row
            subjects.append(subname)
            scores.append(float(score) if score is not None else 0)
            # 直接查字典
            report_content = report_dict.get(tid)
            if report_content:
                reports.append({'subject': subname, 'teacher': tname, 'content': report_content})
            else:
                reports.append({'subject': subname, 'teacher': tname, 'content': '老师正在认真分析此次考试呦...'})
    conn.close()
    return render_template('student/report.html', 
        exam_list=exam_list, 
        selected_exam_id=exam_id, 
        subjects=subjects, 
        scores=scores,
        reports=reports
    )




#################################
#
#
 #       李之爹的领域
#
#
################################


# 教师-查看课表页面（可切换班级，可选只看自己所授科目）
@app.route('/teacher/schedule', methods=['GET'])
def teacher_schedule():
    if session.get('role') != 'teacher':
        return redirect(url_for('login'))
    teacher_name = session.get('name')
    conn = get_conn()
    cursor = conn.cursor()
    # 获取所有班级
    cursor.execute('SELECT class_id, class_name FROM class ORDER BY class_id')
    classes = [{'class_id': r[0], 'class_name': r[1]} for r in cursor.fetchall()]
    current_class_id = request.args.get('class_id') or (classes[0]['class_id'] if classes else None)
    only_self = request.args.get('only_self', '0') == '1'
    # 获取所有课程和教师
    cursor.execute('SELECT subject_id, subject_name FROM subject ORDER BY subject_id')
    subjects = [{'subject_id': r[0], 'subject_name': r[1]} for r in cursor.fetchall()]
    cursor.execute('SELECT teacher_id, name FROM teacher ORDER BY teacher_id')
    teachers = [{'teacher_id': r[0], 'name': r[1]} for r in cursor.fetchall()]
    # 查询当前班级课表
    schedule_map = {}
    if current_class_id:
        if only_self:
            # 查找当前老师id
            cursor.execute('SELECT teacher_id FROM teacher WHERE name=?', teacher_name)
            row = cursor.fetchone()
            teacher_id = row[0] if row else None
            cursor.execute('SELECT week_day, period, subject_id, teacher_id FROM schedule WHERE class_id=? AND teacher_id=?', current_class_id, teacher_id)
        else:
            cursor.execute('SELECT week_day, period, subject_id, teacher_id FROM schedule WHERE class_id=?', current_class_id)
        for r in cursor.fetchall():
            schedule_map[(r[0], r[1])] = {'subject_id': r[2], 'teacher_id': r[3]}
    conn.close()
    weekdays = ['一','二','三','四','五','六','日']
    periods = list(range(1,9))
    return render_template('teacher/schedule.html', schedule_map=schedule_map, classes=classes, current_class_id=current_class_id, subjects=subjects, teachers=teachers, weekdays=weekdays, periods=periods, only_self=only_self)



@app.route('/teacher/profile')
def teacher_profile():
    if session.get('role') != 'teacher':
        return redirect(url_for('login'))
    teacher_name = session.get('name')
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('SELECT name, title, contact_email FROM teacher WHERE name=?', teacher_name)
    row = cursor.fetchone()
    conn.close()
    if row:
        name, title, contact_email = row
    else:
        name, title, contact_email = '', '', ''
    return render_template('teacher/profile.html', name=name, title=title, contact_email=contact_email)


#所教学生档案
@app.route('/teacher/students')
def teacher_students():
    if session.get('role') != 'teacher':
        return redirect(url_for('login'))
    teacher_name = session.get('name')
    conn = get_conn()
    cursor = conn.cursor()
    # 查teacher_id
    cursor.execute('SELECT teacher_id FROM teacher WHERE name=?', teacher_name)
    row = cursor.fetchone()
    if not row:
        conn.close()
        return render_template('teacher/students.html', students=[])
    teacher_id = row[0]
    # 查该老师作为班主任的学生
    cursor.execute('''
        SELECT s.student_id, s.name, c.class_name
        FROM student s
        JOIN class c ON s.class_id = c.class_id
        WHERE c.head_teacher_id = ?
    ''', teacher_id)
    students1 = cursor.fetchall()
    # 查该老师作为任课老师的学生
    cursor.execute('''
        SELECT s.student_id, s.name, c.class_name
        FROM teacher_class_subject tcs
        JOIN class c ON tcs.class_id = c.class_id
        JOIN student s ON s.class_id = c.class_id
        WHERE tcs.teacher_id = ?
    ''', teacher_id)
    students2 = cursor.fetchall()
    # 合并去重
    all_students = { (s[0], s[1], s[2]) for s in students1 + students2 }
    students = list(all_students)
    conn.close()
    return render_template('teacher/students.html', students=students)


#成绩分析与管理score
@app.route('/teacher/score')
def teacher_score():
    if session.get('role') != 'teacher':
        return redirect(url_for('login'))
    teacher_name = session.get('name')
    conn = get_conn()
    cursor = conn.cursor()
    # 查teacher_id
    cursor.execute('SELECT teacher_id FROM teacher WHERE name=?', teacher_name)
    row = cursor.fetchone()
    if not row:
        conn.close()
        return render_template('teacher/score.html', scores=[])
    teacher_id = row[0]
    # 查询该老师所教学生的成绩明细
    cursor.execute('''
        SELECT s.student_id, s.name, c.class_name, sub.subject_name, e.exam_name, es.score
        FROM teacher_class_subject tcs
        JOIN class c ON tcs.class_id = c.class_id
        JOIN student s ON s.class_id = c.class_id
        JOIN subject sub ON tcs.subject_id = sub.subject_id
        JOIN exam_score es ON es.student_id = s.student_id AND es.subject_id = sub.subject_id
        JOIN exam e ON es.exam_id = e.exam_id
        WHERE tcs.teacher_id = ?
        ORDER BY c.class_name, s.name, sub.subject_name, e.exam_date DESC
    ''', teacher_id)
    scores = cursor.fetchall()
    conn.close()
    #调试
    #print('scores:', scores)
    return render_template('teacher/score.html', scores=scores)

@app.route('/teacher/evaluate', methods=['GET'])
def teacher_evaluate():
    if session.get('role') != 'teacher':
        return redirect(url_for('login'))
    teacher_name = session.get('name')
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('SELECT teacher_id FROM teacher WHERE name=?', teacher_name)
    row = cursor.fetchone()
    if not row:
        conn.close()
        return render_template('teacher/evaluate.html', class_list=[], students=[], selected_class=None)
    teacher_id = row[0]
    cursor.execute('''
        SELECT DISTINCT c.class_id, c.class_name
        FROM teacher_class_subject tcs
        JOIN class c ON tcs.class_id = c.class_id
        WHERE tcs.teacher_id = ?
        ORDER BY c.class_id
    ''', teacher_id)
    class_list = cursor.fetchall()
    selected_class = request.args.get('class_id')
    students = []
    if selected_class:
        cursor.execute('''
            SELECT s.student_id, s.name, c.class_name
            FROM student s
            JOIN class c ON s.class_id = c.class_id
            WHERE s.class_id = ?
            ORDER BY s.name
        ''', selected_class)
        students = cursor.fetchall()
    conn.close()
    return render_template('teacher/evaluate.html', class_list=class_list, students=students, selected_class=selected_class)

@app.route('/teacher/evaluate/student/<student_id>', methods=['GET'])
def teacher_evaluate_student(student_id):
    if session.get('role') != 'teacher':
        return redirect(url_for('login'))
    teacher_name = session.get('name')
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.name, c.class_name FROM student s JOIN class c ON s.class_id = c.class_id WHERE s.student_id=?
    ''', student_id)
    stu_row = cursor.fetchone()
    if not stu_row:
        conn.close()
        return '学生不存在'
    stu_name, class_name = stu_row
    cursor.execute('''
        SELECT e.exam_id, e.exam_name, e.exam_date FROM exam_score es JOIN exam e ON es.exam_id = e.exam_id WHERE es.student_id=? GROUP BY e.exam_id, e.exam_name, e.exam_date ORDER BY e.exam_date DESC
    ''', student_id)
    exams = cursor.fetchall()
    cursor.execute('''
        SELECT DISTINCT s.subject_id, s.subject_name FROM exam_score es JOIN subject s ON es.subject_id = s.subject_id WHERE es.student_id=? ORDER BY s.subject_id
    ''', student_id)
    subjects = cursor.fetchall()
    exam_data = []
    for eid, ename, edate in exams:
        row = {'exam_id': eid, 'exam_name': ename, 'exam_date': edate, 'scores': [], 'report': ''}
        for subid, subname in subjects:
            cursor.execute('SELECT score FROM exam_score WHERE student_id=? AND exam_id=? AND subject_id=?', student_id, eid, subid)
            r = cursor.fetchone()
            row['scores'].append({'subject': subname, 'score': r[0] if r else None})
        cursor.execute('SELECT content FROM study_report WHERE student_id=? AND report_date=? AND teacher_id=(SELECT teacher_id FROM teacher WHERE name=?)', student_id, edate, teacher_name)
        rep = cursor.fetchone()
        row['report'] = rep[0] if rep else ''
        # 查询班级均分
        cursor.execute('''
            SELECT AVG(score) FROM exam_score WHERE exam_id=? AND subject_id IN (SELECT subject_id FROM exam_score WHERE student_id=?) AND student_id IN (SELECT student_id FROM student WHERE class_id=(SELECT class_id FROM student WHERE student_id=?))
        ''', eid, student_id, student_id)
        avg_score = cursor.fetchone()[0]
        row['class_avg'] = round(avg_score, 2) if avg_score is not None else None
        # 查询本班所有学生该次考试总分
        cursor.execute('''
            SELECT s.student_id, SUM(es.score) as total
            FROM student s
            JOIN exam_score es ON s.student_id = es.student_id
            WHERE s.class_id = (SELECT class_id FROM student WHERE student_id=?) AND es.exam_id = ?
            GROUP BY s.student_id
        ''', student_id, eid)
        row['class_scores'] = [{'student_id': r[0], 'total': float(r[1]) if r[1] is not None else 0} for r in cursor.fetchall()]
        exam_data.append(row)
    conn.close()
    return render_template('teacher/evaluate_student.html', stu_name=stu_name, class_name=class_name, exam_data=exam_data, student_id=student_id)

@app.route('/teacher/evaluate/report/update', methods=['POST'])
def teacher_evaluate_report_update():
    if session.get('role') != 'teacher':
        return {'status': 0, 'msg': '未登录'}
    teacher_name = session.get('name')
    student_id = request.form.get('student_id')
    exam_date = request.form.get('exam_date')
    content = request.form.get('content', '').strip()
    if not (student_id and exam_date and content):
        return {'status': 0, 'msg': '参数不完整'}
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('SELECT teacher_id FROM teacher WHERE name=?', teacher_name)
    row = cursor.fetchone()
    if not row:
        conn.close()
        return {'status': 0, 'msg': '教师不存在'}
    teacher_id = row[0]
    cursor.execute('SELECT report_id FROM study_report WHERE student_id=? AND teacher_id=? AND report_date=?', student_id, teacher_id, exam_date)
    r = cursor.fetchone()
    if r:
        cursor.execute('UPDATE study_report SET content=? WHERE report_id=?', content, r[0])
    else:
        import uuid
        report_id = str(uuid.uuid4())[:20]
        cursor.execute('INSERT INTO study_report (report_id, student_id, teacher_id, report_date, content, evaluation_level) VALUES (?, ?, ?, ?, ?, ?)', report_id, student_id, teacher_id, exam_date, content, None)
    conn.commit()
    conn.close()
    return {'status': 1, 'msg': '评价已保存'}




    
@app.route('/teacher/class', methods=['GET', 'POST'])
def teacher_class():
    if session.get('role') != 'teacher':
        return redirect(url_for('login'))
    teacher_name = session.get('name')
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('SELECT teacher_id FROM teacher WHERE name=?', teacher_name)
    row = cursor.fetchone()
    if not row:
        conn.close()
        return render_template('teacher/class.html', class_list=[], exam_list=[], scores=[], report=None, selected_class=None, selected_exam=None)
    teacher_id = row[0]
    cursor.execute('''
        SELECT DISTINCT c.class_id, c.class_name
        FROM teacher_class_subject tcs
        JOIN class c ON tcs.class_id = c.class_id
        WHERE tcs.teacher_id = ?
        ORDER BY c.class_id
    ''', teacher_id)
    class_list = cursor.fetchall()
    exam_list = []
    selected_class = request.values.get('class_id')
    selected_exam = request.values.get('exam_id')
    scores = []
    report = None
    if selected_class:
        cursor.execute('''
            SELECT DISTINCT e.exam_id, e.exam_name, e.exam_date
            FROM exam_score es
            JOIN exam e ON es.exam_id = e.exam_id
            JOIN student s ON es.student_id = s.student_id
            WHERE s.class_id = ?
            ORDER BY e.exam_date DESC
        ''', selected_class)
        exam_list = cursor.fetchall()
    else:
        exam_list = []
    if selected_class and selected_exam:
        cursor.execute('''
            SELECT sub.subject_name, AVG(es.score) as avg_score
            FROM exam_score es
            JOIN subject sub ON es.subject_id = sub.subject_id
            JOIN student s ON es.student_id = s.student_id
            WHERE s.class_id = ? AND es.exam_id = ?
            GROUP BY sub.subject_name
            ORDER BY sub.subject_name
        ''', selected_class, selected_exam)
        scores = cursor.fetchall()
        cursor.execute('''
            SELECT content FROM class_exam_report WHERE teacher_id=? AND class_id=? AND exam_id=?
        ''', teacher_id, selected_class, selected_exam)
        report_row = cursor.fetchone()
        report = report_row[0] if report_row else None
        subject_stats = {}
        if selected_class and selected_exam:
            cursor.execute('''
                SELECT DISTINCT sub.subject_name
                FROM exam_score es
                JOIN subject sub ON es.subject_id = sub.subject_id
                JOIN student s ON es.student_id = s.student_id
                WHERE s.class_id = ? AND es.exam_id = ?
            ''', selected_class, selected_exam)
            subject_names = [row[0] for row in cursor.fetchall()]
            for subject in subject_names:
                cursor.execute('''
                    SELECT es.score
                    FROM exam_score es
                    JOIN subject sub ON es.subject_id = sub.subject_id
                    JOIN student s ON es.student_id = s.student_id
                    WHERE s.class_id = ? AND es.exam_id = ? AND sub.subject_name = ?
                ''', selected_class, selected_exam, subject)
                scores_list = [float(r[0]) for r in cursor.fetchall()]
                levels = ['A', 'B', 'C', 'D']
                level_counts = [0, 0, 0, 0]
                for score in scores_list:
                    if score >= 90:
                        level_counts[0] += 1
                    elif score >= 75:
                        level_counts[1] += 1
                    elif score >= 60:
                        level_counts[2] += 1
                    else:
                        level_counts[3] += 1
                cursor.execute('''
                    SELECT e.exam_name, AVG(es.score)
                    FROM exam_score es
                    JOIN exam e ON es.exam_id = e.exam_id
                    JOIN subject sub ON es.subject_id = sub.subject_id
                    JOIN student s ON es.student_id = s.student_id
                    WHERE s.class_id = ? AND sub.subject_name = ?
                    GROUP BY e.exam_name, e.exam_date
                    ORDER BY e.exam_date
                ''', selected_class, subject)
                exam_rows = cursor.fetchall()
                exam_names = [r[0] for r in exam_rows]
                exam_avgs = [float(r[1]) if r[1] is not None else 0 for r in exam_rows]
                subject_stats[subject] = {
                    'levels': levels,
                    'level_counts': level_counts,
                    'exam_names': exam_names,
                    'exam_avgs': exam_avgs
                }
        else:
            subject_stats = {}
    else:
        subject_stats = {}
    conn.close()
    return render_template('teacher/class.html', class_list=class_list, exam_list=exam_list, scores=scores, report=report, selected_class=selected_class, selected_exam=selected_exam, subject_stats=subject_stats)

##########################
#
#
#      领域结束
#
#
##########################







# 班主任主页

# 班主任个人档案-查看
@app.route('/classmaster/profile')
def classmaster_profile():
    if session.get('role') != 'classmaster':
        return redirect(url_for('login'))
    classmaster_name = session.get('name')
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT teacher_id, name, gender, title, contact_email, office_address, phone FROM teacher WHERE name=?
    ''', classmaster_name)
    row = cursor.fetchone()
    if row:
        teacher_id, name, gender, title, contact_email, office_address, phone = row
    else:
        teacher_id, name, gender, title, contact_email, office_address, phone = '', classmaster_name, '', '', '', '', ''
    # 管理班级（班主任）
    cursor.execute('SELECT class_id, class_name FROM class WHERE head_teacher_id=?', teacher_id)
    manage_class_rows = cursor.fetchall()
    manage_classes = [r[1] for r in manage_class_rows]
    # 任教班级（所有该教师授课的班级，包含管理班级）
    cursor.execute('''
        SELECT DISTINCT c.class_id, c.class_name FROM teacher_class_subject tcs
        JOIN class c ON tcs.class_id = c.class_id
        WHERE tcs.teacher_id=? ''', teacher_id)
    teach_class_rows = cursor.fetchall()
    teach_classes = [r[1] for r in teach_class_rows]
    conn.close()
    return render_template('classmaster/profile.html', teacher_id=teacher_id, name=name, gender=gender, title=title, contact_email=contact_email, office_address=office_address, phone=phone, manage_classes=manage_classes, teach_classes=teach_classes)

# 班主任个人档案-编辑
@app.route('/classmaster/profile/edit', methods=['POST'])
def classmaster_profile_edit():
    if session.get('role') != 'classmaster':
        return redirect(url_for('login'))
    classmaster_name = session.get('name')
    conn = get_conn()
    cursor = conn.cursor()
    gender = request.form['gender']
    title = request.form['title']
    contact_email = request.form['contact_email']
    office_address = request.form['office_address']
    phone = request.form['phone']
    cursor.execute('''
        UPDATE teacher SET gender=?, title=?, contact_email=?, office_address=?, phone=? WHERE name=?
    ''', gender, title, contact_email, office_address, phone, classmaster_name)
    conn.commit()
    conn.close()
    flash('个人档案已更新', 'success')
    return redirect(url_for('classmaster_profile'))


# 班主任-学生档案管理-删除学生（将学生班级设为空）
@app.route('/classmaster/student/delete', methods=['POST'])
def classmaster_student_delete():
    if session.get('role') != 'classmaster':
        return redirect(url_for('login'))
    student_id = request.form.get('student_id')
    if not student_id:
        flash('未指定学生', 'danger')
        return redirect(url_for('classmaster_students'))
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('UPDATE student SET class_id=NULL WHERE student_id=?', student_id)
    conn.commit()
    conn.close()
    flash('学生已移出班级', 'success')
    return redirect(url_for('classmaster_students'))

# 班主任-学生档案管理-添加学生（将班级为空的学生加入本班）
@app.route('/classmaster/student/add', methods=['GET', 'POST'])
def classmaster_student_add():
    if session.get('role') != 'classmaster':
        return redirect(url_for('login'))
    classmaster_name = session.get('name')
    conn = get_conn()
    cursor = conn.cursor()
    # 查找班主任所带班级
    cursor.execute('SELECT class_id, class_name FROM class WHERE head_teacher_id = (SELECT teacher_id FROM teacher WHERE name=?)', classmaster_name)
    class_row = cursor.fetchone()
    if not class_row:
        conn.close()
        flash('未找到班级', 'danger')
        return redirect(url_for('classmaster_students'))
    class_id, class_name = class_row
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        if not student_id:
            flash('未选择学生', 'danger')
        else:
            cursor.execute('UPDATE student SET class_id=? WHERE student_id=?', class_id, student_id)
            conn.commit()
            flash('学生已加入班级', 'success')
        conn.close()
        return redirect(url_for('classmaster_students'))
    # GET请求，查找所有班级为空的学生
    cursor.execute('SELECT student_id, name, gender, birth_date, contact_phone, emergency_contact FROM student WHERE class_id IS NULL')
    students = cursor.fetchall()
    conn.close()
    return render_template('classmaster/add_student.html', students=students, class_name=class_name)




# 班主任-学生档案管理
@app.route('/classmaster/students')
def classmaster_students():
    if session.get('role') != 'classmaster':
        return redirect(url_for('login'))
    classmaster_name = session.get('name')
    print('班主任姓名:', classmaster_name)
    try:
        conn = get_conn()
        print('数据库连接成功')
    except Exception as e:
        print('数据库连接失败:', e)
        return '数据库连接失败: ' + str(e)
    cursor = conn.cursor()
    # 查找班主任所带班级（用teacher_id）
    cursor.execute('SELECT class_id, class_name FROM class WHERE head_teacher_id = (SELECT teacher_id FROM teacher WHERE name=?)', classmaster_name)
    class_row = cursor.fetchone()
    print('班级查询结果:', class_row)
    if not class_row:
        conn.close()
        return render_template('classmaster/students.html', students=[], class_name=None)
    class_id, class_name = class_row
    # 查找本班所有学生
    cursor.execute('SELECT student_id, name, gender, birth_date, contact_phone, emergency_contact FROM student WHERE class_id=?', class_id)
    students = cursor.fetchall()
    print('学生查询结果:', students)
    conn.close()
    return render_template('classmaster/students.html', students=students, class_name=class_name)

# 班主任-学生成绩管理

@app.route('/classmaster/scores', methods=['GET', 'POST'])
def classmaster_scores():
    if session.get('role') != 'classmaster':
        return redirect(url_for('login'))
    if request.method == 'POST':
        # 处理成绩更改
        exam_id = request.form.get('exam_id')
        student_name = request.form.get('student_name')
        subject = request.form.get('subject')
        score = request.form.get('score')
        ranking = request.form.get('ranking')
        if not (exam_id and student_name and subject and score and ranking):
            flash('信息不完整', 'danger')
        else:
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute('SELECT student_id FROM student WHERE name=?', student_name)
            stu_row = cursor.fetchone()
            cursor.execute('SELECT subject_id FROM subject WHERE subject_name=?', subject)
            sub_row = cursor.fetchone()
            if not (stu_row and sub_row):
                conn.close()
                flash('查找学生或学科失败', 'danger')
            else:
                student_id = stu_row[0]
                subject_id = sub_row[0]
                cursor.execute('''
                    UPDATE exam_score SET score=?, ranking=?
                    WHERE exam_id=? AND student_id=? AND subject_id=?
                ''', score, ranking, exam_id, student_id, subject_id)
                conn.commit()
                conn.close()
                flash('成绩已更新', 'success')
        return redirect(url_for('classmaster_scores', kw_exam=request.args.get('kw_exam',''), kw_subject=request.args.get('kw_subject','')))
    # GET请求，正常查询
    classmaster_name = session.get('name')
    kw_exam = request.args.get('kw_exam', '').strip()
    kw_subject = request.args.get('kw_subject', '').strip()
    conn = get_conn()
    cursor = conn.cursor()
    # 查找班主任所带班级
    cursor.execute('SELECT class_id, class_name FROM class WHERE head_teacher_id = (SELECT teacher_id FROM teacher WHERE name=?)', classmaster_name)
    class_row = cursor.fetchone()
    if not class_row:
        conn.close()
        return render_template('classmaster/scores.html', exams=[], class_name=None, kw_exam=kw_exam, kw_subject=kw_subject, exam_options=[], subject_options=[])
    class_id, class_name = class_row
    # 获取本班所有考试名
    cursor.execute('''
        SELECT DISTINCT e.exam_name FROM exam_score es
        JOIN exam e ON es.exam_id = e.exam_id
        JOIN student st ON es.student_id = st.student_id
        WHERE st.class_id = ?
        ORDER BY e.exam_name''', class_id)
    exam_options = [r[0] for r in cursor.fetchall()]
    # 获取本班所有学科名
    cursor.execute('''
        SELECT DISTINCT s.subject_name FROM exam_score es
        JOIN subject s ON es.subject_id = s.subject_id
        JOIN student st ON es.student_id = st.student_id
        WHERE st.class_id = ?
        ORDER BY s.subject_name''', class_id)
    subject_options = [r[0] for r in cursor.fetchall()]
    # 查找本班所有学生成绩，按考试分组，并补充班级排名和学校排名
    sql = '''
        SELECT e.exam_id, e.exam_name, e.exam_type, e.exam_date, s.subject_id, s.subject_name, st.student_id, st.name, es.score
        FROM exam_score es
        JOIN exam e ON es.exam_id = e.exam_id
        JOIN subject s ON es.subject_id = s.subject_id
        JOIN student st ON es.student_id = st.student_id
        WHERE st.class_id = ?
    '''
    params = [class_id]
    if kw_exam:
        sql += " AND e.exam_name = ?"
        params.append(kw_exam)
    if kw_subject:
        sql += " AND s.subject_name = ?"
        params.append(kw_subject)
    sql += " ORDER BY e.exam_date DESC, e.exam_id, s.subject_id, st.name"
    cursor.execute(sql, *params)
    rows = cursor.fetchall()
    from collections import defaultdict
    exams = defaultdict(list)
    exam_info = {}
    # 预处理：按(考试id,学科id)分组，分别收集本班和全校成绩
    class_scores = defaultdict(list)  # (exam_id, subject_id) -> list of (student_id, name, score)
    all_scores = defaultdict(list)    # (exam_id, subject_id) -> list of (student_id, name, score)
    for r in rows:
        exam_id = r[0]
        subject_id = r[4]
        student_id = r[6]
        student_name = r[7]
        score = r[8]
        class_scores[(exam_id, subject_id)].append((student_id, student_name, score))
        if exam_id not in exam_info:
            exam_info[exam_id] = {
                'exam_name': r[1],
                'exam_type': r[2],
                'exam_date': r[3]
            }
    # 查询全校同场考试同学科所有成绩
    sql_all = '''
        SELECT e.exam_id, s.subject_id, st.student_id, st.name, es.score
        FROM exam_score es
        JOIN exam e ON es.exam_id = e.exam_id
        JOIN subject s ON es.subject_id = s.subject_id
        JOIN student st ON es.student_id = st.student_id
        WHERE 1=1
    '''
    # 只查本页面涉及到的考试和学科，减少数据量
    exam_ids = list({r[0] for r in rows})
    subject_ids = list({r[4] for r in rows})
    if exam_ids and subject_ids:
        sql_all += f" AND e.exam_id IN ({','.join(['?']*len(exam_ids))}) AND s.subject_id IN ({','.join(['?']*len(subject_ids))})"
        params_all = exam_ids + subject_ids
        cursor.execute(sql_all, *params_all)
        for row in cursor.fetchall():
            all_scores[(row[0], row[1])].append((row[2], row[3], row[4]))
    # 重新遍历rows，生成带排名的成绩
    for r in rows:
        exam_id = r[0]
        subject_id = r[4]
        student_id = r[6]
        student_name = r[7]
        score = r[8]
        # 班级排名
        class_list = sorted(class_scores[(exam_id, subject_id)], key=lambda x: (-x[2], x[1]))
        class_ranking = next((i+1 for i, s in enumerate(class_list) if s[0]==student_id), None)
        # 学校排名
        school_list = sorted(all_scores[(exam_id, subject_id)], key=lambda x: (-x[2], x[1]))
        school_ranking = next((i+1 for i, s in enumerate(school_list) if s[0]==student_id), None)
        exams[exam_id].append({
            'subject': r[5],
            'student_name': student_name,
            'score': score,
            'class_ranking': class_ranking,
            'school_ranking': school_ranking
        })
    exam_list = [
        {
            'exam_id': eid,
            'exam_name': exam_info[eid]['exam_name'],
            'exam_type': exam_info[eid]['exam_type'],
            'exam_date': exam_info[eid]['exam_date'],
            'scores': exams[eid]
        }
        for eid in exam_info
    ]
    conn.close()
    return render_template('classmaster/scores.html', exams=exam_list, class_name=class_name, kw_exam=kw_exam, kw_subject=kw_subject, exam_options=exam_options, subject_options=subject_options)


# 班主任-查看班级课表（与教师端一致）
@app.route('/classmaster/schedule', methods=['GET'])
def classmaster_schedule():
    if session.get('role') != 'classmaster':
        return redirect(url_for('login'))
    classmaster_name = session.get('name')
    conn = get_conn()
    cursor = conn.cursor()
    # 查找班主任id
    cursor.execute('SELECT teacher_id FROM teacher WHERE name=?', classmaster_name)
    row = cursor.fetchone()
    if not row:
        conn.close()
        return render_template('classmaster/schedule.html', schedule_map={}, classes=[], current_class_id=None, subjects=[], teachers=[], weekdays=['一','二','三','四','五','六','日'], periods=list(range(1,9)), only_self=False, active='schedule')
    teacher_id = row[0]
    # 获取所有班级
    cursor.execute('SELECT class_id, class_name FROM class ORDER BY class_id')
    classes = [{'class_id': r[0], 'class_name': r[1]} for r in cursor.fetchall()]
    # 当前选中班级
    current_class_id = request.args.get('class_id') or (classes[0]['class_id'] if classes else None)
    # 是否只看自己所授科目
    only_self = request.args.get('only_self', '0') == '1'
    # 获取所有课程和教师
    cursor.execute('SELECT subject_id, subject_name FROM subject ORDER BY subject_id')
    subjects = [{'subject_id': r[0], 'subject_name': r[1]} for r in cursor.fetchall()]
    cursor.execute('SELECT teacher_id, name FROM teacher ORDER BY teacher_id')
    teachers = [{'teacher_id': r[0], 'name': r[1]} for r in cursor.fetchall()]
    # 查询本班主任所授学科id集合
    cursor.execute('SELECT subject_id FROM teacher WHERE teacher_id=?', teacher_id)
    teacher_subject_row = cursor.fetchone()
    teacher_subject_ids = set()
    if teacher_subject_row and teacher_subject_row[0]:
        teacher_subject_ids.add(teacher_subject_row[0])
    # 查询当前班级课表
    schedule_map = {}
    if current_class_id:
        cursor.execute('SELECT week_day, period, subject_id, teacher_id FROM schedule WHERE class_id=?', current_class_id)
        for r in cursor.fetchall():
            # 只看自己所授科目时过滤
            if only_self and r[2] not in teacher_subject_ids:
                continue
            schedule_map[(r[0], r[1])] = {'subject_id': r[2], 'teacher_id': r[3]}
    conn.close()
    weekdays = ['一','二','三','四','五','六','日']
    periods = list(range(1,9))



    return render_template('classmaster/schedule.html', schedule_map=schedule_map, classes=classes, current_class_id=current_class_id, subjects=subjects, teachers=teachers, weekdays=weekdays, periods=periods, only_self=only_self, active='schedule')

# 班主任-学生成绩详情
@app.route('/classmaster/score_detail/<student_id>')
def classmaster_score_detail(student_id):
    if session.get('role') != 'classmaster':
        return redirect(url_for('login'))
    kw = request.args.get('kw', '').strip()
    conn = get_conn()
    cursor = conn.cursor()
    # 查学生基本信息
    cursor.execute('SELECT name FROM student WHERE student_id=?', student_id)
    stu_row = cursor.fetchone()
    if not stu_row:
        conn.close()
        return render_template('classmaster/score_detail.html', student={'name': '未知'}, exam_list=[], kw=kw)
    student = {'student_id': student_id, 'name': stu_row[0]}
    # 查成绩
    sql = '''
        SELECT e.exam_name, e.exam_type, e.exam_date, s.subject_name, es.score, es.ranking
        FROM exam_score es
        JOIN exam e ON es.exam_id = e.exam_id
        JOIN subject s ON es.subject_id = s.subject_id
        WHERE es.student_id = ?
    '''
    params = [student_id]
    if kw:
        sql += " AND e.exam_name LIKE ?"
        params.append(f'%{kw}%')
    sql += " ORDER BY e.exam_date DESC, s.subject_id"
    cursor.execute(sql, *params)
    rows = cursor.fetchall()
    from collections import defaultdict
    exams = defaultdict(list)
    for r in rows:
        key = (r[0], r[1], r[2])
        exams[key].append({'subject': r[3], 'score': r[4], 'ranking': r[5]})
    exam_list = [
        {'exam_name': k[0], 'exam_type': k[1], 'exam_date': k[2], 'scores': v}
        for k, v in exams.items()
    ]
    conn.close()
    return render_template('classmaster/score_detail.html', student=student, exam_list=exam_list, kw=kw)

# 班主任-学生学习情况

# 班主任-学生学习情况（含学生搜索与报告）
@app.route('/classmaster/analysis')
def classmaster_analysis():
    if session.get('role') != 'classmaster':
        return redirect(url_for('login'))
    classmaster_name = session.get('name')
    kw = request.args.get('kw', '').strip()
    student_id = request.args.get('student_id', '').strip()
    conn = get_conn()
    cursor = conn.cursor()
    # 查找班主任所带班级
    cursor.execute('SELECT class_id, class_name FROM class WHERE head_teacher_id = (SELECT teacher_id FROM teacher WHERE name=?)', classmaster_name)
    class_row = cursor.fetchone()
    if not class_row:
        conn.close()
        return render_template('classmaster/analysis.html', students=[], class_name=None, kw=kw, selected_student=None, report_data=None)
    class_id, class_name = class_row
    # 查找本班所有学生
    if kw:
        cursor.execute('SELECT student_id, name FROM student WHERE class_id=? AND name LIKE ?', class_id, f'%{kw}%')
    else:
        cursor.execute('SELECT student_id, name FROM student WHERE class_id=?', class_id)
    students = [{'student_id': r[0], 'name': r[1]} for r in cursor.fetchall()]
    selected_student = None
    report_data = None
    if student_id:
        # 查找学生信息
        cursor.execute('SELECT student_id, name FROM student WHERE student_id=? AND class_id=?', student_id, class_id)
        stu_row = cursor.fetchone()
        if stu_row:
            selected_student = {'student_id': stu_row[0], 'name': stu_row[1]}
            # 查询该学生近期学习报告（复用学生端report逻辑）
            exam_id = request.args.get('exam_id')
            # 查询所有考试（按时间降序）
            cursor.execute('''
                SELECT DISTINCT e.exam_id, e.exam_name, e.exam_date
                FROM exam_score es
                JOIN exam e ON es.exam_id = e.exam_id
                WHERE es.student_id = ?
                ORDER BY e.exam_date DESC
            ''', stu_row[0])
            exams = cursor.fetchall()
            exam_list = [
                {'exam_id': row[0], 'exam_name': row[1], 'exam_date': str(row[2])}
                for row in exams
            ]
            # 默认选中最新一次考试
            if not exam_id and exam_list:
                exam_id = str(exam_list[0]['exam_id'])
            # 查询该考试下所有学科及成绩
            subjects, scores, reports = [], [], []
            if exam_id:
                # 先查考试日期
                cursor.execute('SELECT exam_date FROM exam WHERE exam_id=?', exam_id)
                exam_date_row = cursor.fetchone()
                if exam_date_row:
                    from datetime import datetime, timedelta
                    exam_date = exam_date_row[0]
                    if isinstance(exam_date, str):
                        exam_date = datetime.strptime(exam_date, '%Y-%m-%d')
                    date_start = (exam_date - timedelta(days=3)).strftime('%Y-%m-%d')
                    date_end = (exam_date + timedelta(days=3)).strftime('%Y-%m-%d')
                else:
                    date_start = date_end = None
                # 查询所有学科、成绩、教师id、教师姓名
                cursor.execute('''
                    SELECT s.subject_id, s.subject_name, es.score, t.teacher_id, t.name
                    FROM exam_score es
                    JOIN subject s ON es.subject_id = s.subject_id
                    LEFT JOIN teacher t ON t.subject_id = s.subject_id
                    WHERE es.student_id = ? AND es.exam_id = ?
                    ORDER BY s.subject_id
                ''', stu_row[0], exam_id)
                rows = cursor.fetchall()
                # 查询本学生在本考试前后3天内所有老师的报告，放入字典
                report_dict = {}
                if date_start and date_end:
                    cursor.execute('''
                        SELECT teacher_id, content FROM study_report WHERE student_id=? AND report_date>=? AND report_date<=?
                    ''', stu_row[0], date_start, date_end)
                    for tid, content in cursor.fetchall():
                        report_dict[tid] = content
                for row in rows:
                    subid, subname, score, tid, tname = row
                    subjects.append(subname)
                    scores.append(float(score) if score is not None else 0)
                    report_content = report_dict.get(tid)
                    if report_content:
                        reports.append({'subject': subname, 'teacher': tname, 'content': report_content})
                    else:
                        reports.append({'subject': subname, 'teacher': tname, 'content': '老师正在认真分析此次考试呦...'})
            report_data = {
                'exam_list': exam_list,
                'selected_exam_id': exam_id,
                'subjects': subjects,
                'scores': scores,
                'reports': reports
            }
    conn.close()
    return render_template('classmaster/analysis.html', students=students, class_name=class_name, kw=kw, selected_student=selected_student, report_data=report_data)

# 班主任-成绩分析与管理
@app.route('/classmaster/score')
def classmaster_score():
    if session.get('role') != 'classmaster':
        return redirect(url_for('login'))
    # 这里可以后续扩展分析功能，暂时只渲染页面
    return render_template('classmaster/score.html')

# 班主任-更改学生成绩
@app.route('/classmaster/edit_score', methods=['POST'])
def classmaster_edit_score():
    if session.get('role') != 'classmaster':
        return redirect(url_for('login'))
    exam_id = request.form.get('exam_id')
    student_name = request.form.get('student_name')
    subject = request.form.get('subject')
    score = request.form.get('score')
    ranking = request.form.get('ranking')
    if not (exam_id and student_name and subject and score and ranking):
        flash('信息不完整', 'danger')
        return redirect(url_for('classmaster_scores'))
    conn = get_conn()
    cursor = conn.cursor()
    # 查找 student_id, subject_id
    cursor.execute('SELECT student_id FROM student WHERE name=?', student_name)
    stu_row = cursor.fetchone()
    cursor.execute('SELECT subject_id FROM subject WHERE subject_name=?', subject)
    sub_row = cursor.fetchone()
    if not (stu_row and sub_row):
        conn.close()
        flash('查找学生或学科失败', 'danger')
        return redirect(url_for('classmaster_scores'))
    student_id = stu_row[0]
    subject_id = sub_row[0]
    # 更新成绩
    cursor.execute('''
        UPDATE exam_score SET score=?, ranking=?
        WHERE exam_id=? AND student_id=? AND subject_id=?
    ''', score, ranking, exam_id, student_id, subject_id)
    conn.commit()
    conn.close()
    flash('成绩已更新', 'success')
    return redirect(url_for('classmaster_scores'))




##################
# classmaster evaluate
####################

# 班主任-学生成绩评价入口（与教师端 teacher/evaluate 一致，限定本班）
@app.route('/classmaster/evaluate', methods=['GET'])
def classmaster_evaluate():
    if session.get('role') != 'classmaster':
        return redirect(url_for('login'))
    classmaster_name = session.get('name')
    print('班主任姓名:', classmaster_name)
    conn = get_conn()
    cursor = conn.cursor()
    # 查找班主任所带班级
    cursor.execute('SELECT teacher_id FROM teacher WHERE name=?', classmaster_name)
    row = cursor.fetchone()
    print('teacher_id查询结果:', row)
    if not row:
        conn.close()
        print('未查到班主任teacher_id')
        return render_template('classmaster/evaluate.html', class_list=[], students=[], selected_class=None)
    teacher_id = row[0]
    cursor.execute('SELECT class_id, class_name FROM class WHERE head_teacher_id=?', teacher_id)
    class_list = cursor.fetchall()
    print('班级列表:', class_list)
    selected_class = request.args.get('class_id')
    # 如果未选中班级且有班级，自动选中第一个班级并重定向
    if not selected_class and class_list:
        first_class_id = str(class_list[0][0])
        conn.close()
        return redirect(url_for('classmaster_evaluate', class_id=first_class_id))
    students = []
    if selected_class:
        cursor.execute('''
            SELECT s.student_id, s.name, c.class_name
            FROM student s
            JOIN class c ON s.class_id = c.class_id
            WHERE s.class_id = ?
            ORDER BY s.name
        ''', selected_class)
        students = cursor.fetchall()
        print('学生列表:', students)
    conn.close()
    return render_template('classmaster/evaluate.html', class_list=class_list, students=students, selected_class=selected_class)

@app.route('/classmaster/evaluate/student/<student_id>', methods=['GET'])
def classmaster_evaluate_student(student_id):
    if session.get('role') != 'classmaster':
        return redirect(url_for('login'))
    classmaster_name = session.get('name')
    conn = get_conn()
    cursor = conn.cursor()
    # 查找学生基本信息及班级
    cursor.execute('''
        SELECT s.name, c.class_name FROM student s JOIN class c ON s.class_id = c.class_id WHERE s.student_id=?
    ''', student_id)
    stu_row = cursor.fetchone()
    if not stu_row:
        conn.close()
        return '学生不存在'
    stu_name, class_name = stu_row
    # 查找该学生所有考试
    cursor.execute('''
        SELECT e.exam_id, e.exam_name, e.exam_date FROM exam_score es JOIN exam e ON es.exam_id = e.exam_id WHERE es.student_id=? GROUP BY e.exam_id, e.exam_name, e.exam_date ORDER BY e.exam_date DESC
    ''', student_id)
    exams = cursor.fetchall()
    # 查找该学生所有学科
    cursor.execute('''
        SELECT DISTINCT s.subject_id, s.subject_name FROM exam_score es JOIN subject s ON es.subject_id = s.subject_id WHERE es.student_id=? ORDER BY s.subject_id
    ''', student_id)
    subjects = cursor.fetchall()
    exam_data = []
    for eid, ename, edate in exams:
        row = {'exam_id': eid, 'exam_name': ename, 'exam_date': edate, 'scores': [], 'report': ''}
        for subid, subname in subjects:
            cursor.execute('SELECT score FROM exam_score WHERE student_id=? AND exam_id=? AND subject_id=?', student_id, eid, subid)
            r = cursor.fetchone()
            row['scores'].append({'subject': subname, 'score': r[0] if r else None})
        # 班主任评价（可选：可扩展为班主任评价内容）
        cursor.execute('SELECT content FROM study_report WHERE student_id=? AND report_date=? AND teacher_id=(SELECT teacher_id FROM teacher WHERE name=?)', student_id, edate, classmaster_name)
        rep = cursor.fetchone()
        row['report'] = rep[0] if rep else ''
        # 查询班级均分
        cursor.execute('''
            SELECT AVG(score) FROM exam_score WHERE exam_id=? AND subject_id IN (SELECT subject_id FROM exam_score WHERE student_id=?) AND student_id IN (SELECT student_id FROM student WHERE class_id=(SELECT class_id FROM student WHERE student_id=?))
        ''', eid, student_id, student_id)
        avg_score = cursor.fetchone()[0]
        row['class_avg'] = round(avg_score, 2) if avg_score is not None else None
        # 查询本班所有学生该次考试总分
        cursor.execute('''
            SELECT s.student_id, SUM(es.score) as total
            FROM student s
            JOIN exam_score es ON s.student_id = es.student_id
            WHERE s.class_id = (SELECT class_id FROM student WHERE student_id=?) AND es.exam_id = ?
            GROUP BY s.student_id
        ''', student_id, eid)
        row['class_scores'] = [{'student_id': r[0], 'total': float(r[1]) if r[1] is not None else 0} for r in cursor.fetchall()]
        exam_data.append(row)
    conn.close()
    return render_template('classmaster/evaluate_student.html', stu_name=stu_name, class_name=class_name, exam_data=exam_data, student_id=student_id)



#################
#end
################


# 班主任-学生成绩评价详情-保存评价（与教师端一致，权限为班主任）
@app.route('/classmaster/evaluate/report/update', methods=['POST'])
def classmaster_evaluate_report_update():
    if session.get('role') != 'classmaster':
        return {'status': 0, 'msg': '未登录'}
    classmaster_name = session.get('name')
    student_id = request.form.get('student_id')
    exam_date = request.form.get('exam_date')
    content = request.form.get('content', '').strip()
    if not (student_id and exam_date and content):
        return {'status': 0, 'msg': '参数不完整'}
    conn = get_conn()
    cursor = conn.cursor()
    # 获取班主任teacher_id
    cursor.execute('SELECT teacher_id FROM teacher WHERE name=?', classmaster_name)
    row = cursor.fetchone()
    if not row:
        conn.close()
        return {'status': 0, 'msg': '班主任不存在'}
    teacher_id = row[0]
    # 检查该学生是否属于本班
    cursor.execute('SELECT class_id FROM student WHERE student_id=?', student_id)
    stu_row = cursor.fetchone()
    if not stu_row:
        conn.close()
        return {'status': 0, 'msg': '学生不存在'}
    student_class_id = stu_row[0]
    cursor.execute('SELECT class_id FROM class WHERE head_teacher_id=?', teacher_id)
    class_row = cursor.fetchone()
    if not class_row or class_row[0] != student_class_id:
        conn.close()
        return {'status': 0, 'msg': '无权评价非本班学生'}
    # 查找是否已有评价
    cursor.execute('SELECT report_id FROM study_report WHERE student_id=? AND teacher_id=? AND report_date=?', student_id, teacher_id, exam_date)
    r = cursor.fetchone()
    if r:
        cursor.execute('UPDATE study_report SET content=? WHERE report_id=?', content, r[0])
    else:
        import uuid
        report_id = str(uuid.uuid4())[:20]
        cursor.execute('INSERT INTO study_report (report_id, student_id, teacher_id, report_date, content, evaluation_level) VALUES (?, ?, ?, ?, ?, ?)', report_id, student_id, teacher_id, exam_date, content, None)
    conn.commit()
    conn.close()
    return {'status': 1, 'msg': '评价已保存'}

if __name__ == '__main__':
    app.run(debug=True)