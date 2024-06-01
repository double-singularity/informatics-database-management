from flask import Flask, render_template, request, session, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from db import Database

app = Flask(__name__)
app.config["SECRET_KEY"] = "12345678"


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
        return "<h1>this is homepage</h1>"
    return redirect(url_for('login'))


# @app.route("/login", methods=["GET", "POST"])
# def login():
#     user = request.form['username']
#     password = request.form['password']
    
#     if user == username and check_password_hash(hashed_password, password):
#         flash('Login successful!', 'success')
#         return redirect(url_for('index'))
#     else:
#         flash('Invalid username or password', 'danger')
#     return render_template('login.html')

# @app.route("login/check", methods=["POST"])


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