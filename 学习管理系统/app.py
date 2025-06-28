from flask import Flask, render_template, request, redirect, url_for, flash, session
import pyodbc

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
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        name = request.form['name']
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM [user] WHERE username=?", username)
        if cursor.fetchone():
            flash('用户名已存在', 'danger')
            conn.close()
            return redirect(url_for('register'))
        cursor.execute(
            "INSERT INTO [user] (username, password, role, name) VALUES (?, ?, ?, ?)",
            username, password, role, name
        )
        conn.commit()
        conn.close()
        flash('注册成功，请登录', 'success')
        return redirect(url_for('login'))
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
            elif user[2] == 'classmaster':
                return redirect(url_for('classmaster_profile'))
        else:
            flash('用户名或密码错误', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

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
        SELECT s.name, s.gender, s.birth_date, c.class_name, s.contact_phone, s.emergency_contact
        FROM student s
        JOIN class c ON s.class_id = c.class_id
        WHERE s.student_id = ?
    ''', student_id)
    row = cursor.fetchone()
    conn.close()
    info = {
        'name': row[0],
        'gender': row[1],
        'birth_date': row[2],
        'class_name': row[3],
        'contact_phone': row[4],
        'emergency_contact': row[5]
    } if row else {}
    return render_template('student/profile.html', info=info)

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
    contact_phone = request.form['contact_phone']
    emergency_contact = request.form['emergency_contact']
    cursor.execute('''
        UPDATE student SET name=?, gender=?, birth_date=?, contact_phone=?, emergency_contact=? WHERE student_id=?
    ''', name, gender, birth_date, contact_phone, emergency_contact, student_id)
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
    conn.close()
    from collections import defaultdict
    exams = defaultdict(list)
    for r in rows:
        key = (r[0], r[1], r[2])
        exams[key].append({'subject': r[3], 'score': r[4], 'ranking': r[5]})
    exam_list = [
        {'exam_name': k[0], 'exam_type': k[1], 'exam_date': k[2], 'scores': v}
        for k, v in exams.items()
    ]
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

# 教师主页
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

# 班主任主页
@app.route('/classmaster/profile')
def classmaster_profile():
    if session.get('role') != 'classmaster':
        return redirect(url_for('login'))
    return render_template('classmaster/profile.html', name=session.get('name'))

if __name__ == '__main__':
    app.run(debug=True)
