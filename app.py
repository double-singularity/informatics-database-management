from flask import Flask, render_template, request, session, redirect, url_for
from db import Database

app = Flask(__name__)
app.config["SECRET_KEY"] = "12345678"

db = Database()

def mat_print(mat):
    for thing in mat:
        print(thing)

@app.route("/", methods=["POST", "GET"])
def home():
    return render_template("index.html")

@app.route("/administrator")
def administrator():
    return render_template("administrator.html")

@app.route("/homepage")
def homepage():
    return "<h1>this is homepage</h1>"

@app.route("/display/<table_name>", methods=["POST", "GET"])
def display(table_name):
    return render_template("display.html", my_list=db.exec(f"SELECT * FROM {table_name}"))

@app.route('/view/<table_name>')
def view_table(table_name):
    columns = db.exec(f"DESCRIBE {table_name}")
    first_columns = []
    for thing in columns:
        first_columns.append(thing[0])
    print(first_columns)
    return render_template('view_table.html', table_name=table_name, rows=db.exec(f"SELECT * FROM {table_name}"), first_columns=first_columns)
