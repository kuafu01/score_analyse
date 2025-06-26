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
                return redirect(url_for('student_home'))
            elif user[2] == 'teacher':
                return redirect(url_for('teacher_home'))
            elif user[2] == 'classmaster':
                return redirect(url_for('classmaster_home'))
        else:
            flash('用户名或密码错误', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# 学生模块
@app.route('/student')
def student_home():
    if session.get('role') != 'student':
        return redirect(url_for('login'))
    student_id = session.get('user_id')
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM [user] WHERE user_id=?', student_id)
    stu_username = cursor.fetchone()
    if not stu_username:
        conn.close()
        return render_template('student/student.html', info={})
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
    return render_template('student/student.html', info=info)

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
        return redirect(url_for('student_home'))
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
    return redirect(url_for('student_home'))

@app.route('/student/score')
def student_score():
    if session.get('role') != 'student':
        return redirect(url_for('login'))
    student_id = session.get('username')
    kw = request.args.get('kw', '').strip()
    conn = get_conn()
    cursor = conn.cursor()
    # 查询所有考试及成绩
    sql = '''
        SELECT e.exam_name, e.exam_type, e.exam_date, s.subject_name, es.score, es.ranking
        FROM exam_score es
        JOIN exam e ON es.exam_id = e.exam_id
        JOIN subject s ON es.subject_id = s.subject_id
        WHERE es.student_id = ?
    '''
    params = [student_id]
    if kw:
        sql += " AND (e.exam_name LIKE ? OR s.subject_name LIKE ?)"
        params.extend([f'%{kw}%', f'%{kw}%'])
    sql += " ORDER BY e.exam_date DESC, s.subject_id"
    cursor.execute(sql, *params)
    rows = cursor.fetchall()
    conn.close()
    # 分组整理数据
    from collections import defaultdict
    exams = defaultdict(list)
    for r in rows:
        key = (r[0], r[1], r[2])
        exams[key].append({'subject': r[3], 'score': r[4], 'ranking': r[5]})
    exam_list = [
        {'exam_name': k[0], 'exam_type': k[1], 'exam_date': k[2], 'scores': v}
        for k, v in exams.items()
    ]
    return render_template('student/panel_score.html', exam_list=exam_list)

# 教师主页
@app.route('/teacher')
def teacher_home():
    if session.get('role') != 'teacher':
        return redirect(url_for('login'))
    return render_template('teacher/teacher.html', name=session.get('name'))

# 班主任主页
@app.route('/classmaster')
def classmaster_home():
    if session.get('role') != 'classmaster':
        return redirect(url_for('login'))
    return render_template('classmaster/classmaster.html', name=session.get('name'))

if __name__ == '__main__':
    app.run(debug=True)
