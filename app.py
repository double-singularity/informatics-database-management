from flask import Flask, render_template, request, session, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta
from db import Database


app = Flask(__name__)
app.config["SECRET_KEY"] = "12345678"
app.permanent_session_lifetime = timedelta(minutes=10)


db = Database()
db.connect()


def mat_print(mat):
    for thing in mat:
        print(thing)


@app.route("/", methods=["POST", "GET"])
def home():
    return render_template("index.html")


@app.route("/homepage")
def homepage():
    if 'username' in session:
        return "<h1>welcome</h1>"
    return redirect(url_for('login'))


@app.route("/login", methods=["GET", "POST"])
def login():
    value = session.get('value', None)
    if value not in ['Admin', 'Mahasiswa']:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        value = value.lower()
        if value == "mahasiswa":
            holder = "name"
        elif value == "admin":
            holder

        if username and password:
            db.connect()
            try:
                query = f"SELECT * FROM {value} WHERE {holder} = %s"
                user = db.fetch_data(query, (username,))

                for i in range(len(user)):
                    if user and check_password_hash(user[i]['password'], password):
                        session['username'] = username
                        return redirect(url_for('dashboard'))
    
                flash('Invalid credentials, please try again.')
            finally:
                db.disconnect()
            return redirect(url_for('login'))

    return render_template('login.html', value=value)


@app.route('/view/<table_name>', methods=["POST", "GET"])
def view_table(table_name):
    # if 'username' in session:
        # Use a parameterized query to describe the table
    columns = db.fetch_data("DESCRIBE `%s`" % table_name)
    first_columns = [thing[0] for thing in columns]

    # Fetch all rows from the table
    rows = db.fetch_data("SELECT * FROM `%s`" % table_name)

    return render_template('view_table.html', 
                            table_name=table_name, 
                            rows=rows, 
                            first_columns=first_columns)
    
    return redirect(url_for('login'))

# page not found
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', message="404 Page Not Found"), 404