from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta
from db import Database


app = Flask(__name__)
app.config["SECRET_KEY"] = "12345678"
app.permanent_session_lifetime = timedelta(minutes=15)


db = Database()
db.connect()


def get_sidebar_list(table_name):
    if table_name.lower() == 'admin':
        sidebar_list = ["mahasiswa", "biodata", "log"]
    elif table_name.lower() == 'mahasiswa':
        sidebar_list = ["biodata", "nilai", "jadwal"]

    sidebar_list = [(sidebar_list[i], sidebar_list[i].title()) for i in range(len(sidebar_list))]

    return sidebar_list


@app.route("/", methods=["POST", "GET"])
def home():
    return render_template("index.html")


@app.route('/set_value', methods=['POST'])
def set_value():
    data = request.get_json()
    value = data.get('value')
    if value in ['Admin', 'Mahasiswa']:
        session['value'] = value
        return '', 200
    else:
        return '', 400


@app.route("/login", methods=["GET", "POST"])
def login():
    value = session.get('value', None)
    if value not in ['Admin', 'Mahasiswa']:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        value = value.lower()

        if username and password:
            db.connect()
            try:
                query = f"SELECT * FROM {value} WHERE username = %s"
                user = db.fetch_data(query, (username,))

                if user and check_password_hash(user[0]['password'], password):
                    session['username'] = username
                    if value == "admin":
                        session['admin'] = username
                    return redirect(url_for('dashboard'))
    
                flash('Invalid credentials, please try again')
            finally:
                db.disconnect()
            return redirect(url_for('login'))

    return render_template('login.html', value=value)


@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session.get('username', 'Guest')
    value = session.get('value', 'Guest')


    if value not in ['Admin', 'Mahasiswa']:
        return redirect(url_for('home'))

    table_name = value
    sidebar_list = get_sidebar_list(session.get('value', None))
    session['sidebar'] = sidebar_list
    
    return render_template('dashboard.html', username=username, table_name=table_name, sidebar_list=sidebar_list)


@app.route('/mahasiswa')
def mahasiswa():
    db.connect()
    mahasiswa = db.fetch_data("SELECT * FROM mahasiswa")
    db.disconnect()

    sidebar_list = get_sidebar_list(session.get('value', None))

    return render_template('mahasiswa.html', mahasiswa=mahasiswa, sidebar_list=sidebar_list)


@app.route('/chart-data')
def chart_data():
    data = {
        "categories": [i+1 for i in range(12)],
        "values": session.get("transcript", [])
    }
    return jsonify(data)


@app.route('/nilai')
def nilai():
    db.connect()

    username = session.get('username', None)

    nim = db.fetch_data(f"SELECT nim FROM mahasiswa WHERE username = '{username}'")
  
    transcript = db.fetch_data(f"""
                                SELECT * FROM transcript_nilai 
                                WHERE mahasiswa_nim = '{nim[0]['nim']}'
                                ORDER BY semester ASC
                                """)

    db.disconnect()

    session['transcript'] = [transcript[i]['nilai'] for i in range(len(transcript))]

    sidebar_list = get_sidebar_list(session.get('value', None))

    return render_template('nilai.html', sidebar_list=sidebar_list, username=session.get('username'))


@app.route('/jadwal')
def jadwal():
    sidebar_list = get_sidebar_list(session.get('value', None))
    return render_template('jadwal.html', sidebar_list=sidebar_list)


@app.route('/biodata')
def biodata():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    db.connect()

    value = session.get('value', 'Guest')

    if value not in ['Admin', 'Mahasiswa']:
        return redirect(url_for('home'))
    
    if value == 'Admin':
        biodata = db.fetch_data('''SELECT m.username, b.asal_sekolah, b.status_kelulusan, b.Gender 
                                FROM biodata b, mahasiswa m 
                                WHERE b.nim_mahasiswa = m.nim;''')
    elif value == 'Mahasiswa':
        biodata = db.fetch_data(f'''SELECT m.username, b.asal_sekolah, b.status_kelulusan, b.Gender 
                                FROM biodata b, mahasiswa m 
                                WHERE b.nim_mahasiswa = m.nim
                                AND m.username = "{session.get('username')}";''')
        
    db.disconnect()

    print(biodata)

    sidebar_list = get_sidebar_list(session.get('value', None))

    return render_template('biodata.html', biodata=biodata, sidebar_list=sidebar_list)


@app.route('/create_student', methods=['GET', 'POST'])
def create_student():
    sidebar_list = session.get('sidebar')
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        try:
            db.connect()
            password = generate_password_hash(name.replace(" ", "") + "123")
            db.execute_query("INSERT INTO mahasiswa (username, email, password) VALUES (%s, %s, %s)", (name, email, password))
        except Exception as e:
            print(f"Error: {e}")
        finally:
            db.disconnect()
        return redirect('/mahasiswa')
    return render_template('create_student.html', sidebar_list=sidebar_list)


@app.route('/edit_mahasiswa/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    db.connect()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        db.execute_query("UPDATE mahasiswa SET username=%s, email=%s WHERE nim=%s", (name, email, id))
        db.disconnect()
        return redirect('/mahasiswa')
    student = db.fetch_data("SELECT * FROM mahasiswa WHERE nim=%s", (id,))
    db.disconnect()
    return render_template('edit_mahasiswa.html', student=student[0])


@app.route('/delete_mahasiswa/<int:id>', methods=['POST'])
def delete_mahasiswa(id):
    try:
        db.connect()
        db.execute_query("DELETE FROM biodata WHERE nim_mahasiswa=%s", (id,))
        db.execute_query("DELETE FROM transcript_nilai WHERE nim_mahasiswa=%s", (id,))
        db.execute_query("DELETE FROM mahasiswa WHERE nim=%s", (id,))
    finally:
        db.disconnect()
    return redirect('/mahasiswa')


@app.route('/log', methods=['GET', 'POST'])
def log():
    db.connect()
    mahasiswa_log = db.fetch_data("SELECT * FROM mahasiswa_log")
    mahasiswa_delete_log = db.fetch_data("SELECT * FROM mahasiswa_delete_log")
    db.disconnect()

    texts = []
    for things in mahasiswa_log:
        texts += [f"email changed from {things['old_email']} to {things['new_email']} changed at {things['changed_at']}"]

    # print(mahasiswa_delete_log)

    for things in mahasiswa_delete_log:
        texts += [f"username {things['username']} with nim {things['nim']} deleted at {things['deleted_at']}"]

    # print(texts)

    sidebar_list = get_sidebar_list(session.get('value', None))

    return render_template('log.html', texts=texts, sidebar_list=sidebar_list)


# page not found
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', message=e), 404


if __name__ == '__main__':
    app.run(port=1337, debug=True)



