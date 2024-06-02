from flask import Flask, render_template, request, session, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta
from db import Database


app = Flask(__name__)
app.config["SECRET_KEY"] = "12345678"
app.permanent_session_lifetime = timedelta(minutes=10)


db = Database()
db.connect()


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

                print(user)

                print("check: ", check_password_hash(user[0]['password'], password))

                if user and check_password_hash(user[0]['password'], password):
                    session['username'] = username
                    if value == "admin":
                        session['admin'] = username
                    return redirect(url_for('dashboard'))
    
                flash('Invalid credentials, please try again.')
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

    sidebar_list = []
    
    if table_name.lower() == 'admin':
        sidebar_list = ["mahasiswa", "biodata", "nilai", "jadwal", "matakuliah", "log"]
    elif table_name.lower() == 'mahasiswa':
        sidebar_list = ["biodata", "nilai", "jadwal", "matakuliah"]

    sidebar_list = [(sidebar_list[i], sidebar_list[i].title()) for i in range(len(sidebar_list))]

    session['sidebar'] = sidebar_list
    
    return render_template('dashboard.html', username=username, table_name=table_name, sidebar_list=sidebar_list)

@app.route('/mahasiswa')
def view_students():
    db.connect()
    mahasiswa = db.fetch_data("SELECT * FROM mahasiswa")
    db.disconnect()
    return render_template('mahasiswa.html', mahasiswa=mahasiswa)

@app.route('/view', methods=["POST", "GET"])
def view():
    return render_template('view.html', entries=["admin", "biodata", "mahasiswa", "nilai_mahasiswa", "orang_tua", "users"])

@app.route('/view/<table_name>', methods=["POST", "GET"])
def view_table(table_name):
    if 'admin' in session:  # Check if user is logged in
        try:
            # Connect to the database
            db.connect()

            # Use safe string formatting to include table name in the query
            columns_query = f"DESCRIBE `{table_name}`"
            columns = db.fetch_data(columns_query)
            first_columns = [column['Field'] for column in columns]

            rows_query = f"SELECT * FROM `{table_name}`"
            rows = db.fetch_data(rows_query)
        except Exception as e:
            # Handle database query errors gracefully
            error_message = f"An error occurred while fetching data: {e}"
            return render_template('error.html', error_message=error_message)
        finally:
            db.disconnect()

        return render_template('view_table.html', 
                               table_name=table_name, 
                               rows=rows, 
                               first_columns=first_columns)
    else:
        # Redirect to login page if user is not logged in
        return redirect(url_for('login'))
    

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


# page not found
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', message=e), 404

if __name__ == '__main__':
    app.run(port=1337, debug=True)