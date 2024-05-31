from flask import Flask, render_template, request, session, redirect, url_for
from db import Database

app = Flask(__name__)
app.config["SECRET_KEY"] = "12345678"

db = Database()

@app.route("/", methods=["POST", "GET"])
def home():
    return render_template("index.html")

@app.route("/administrator")
def administrator():
    return 'test'

@app.route("/homepage")
def homepage():
    return "<h1>this is homepage</h1>"

@app.route("/display", methods=["POST", "GET"])
def display():
    return render_template("display.html", my_list=db.exec("SELECT * FROM mahasiswa"))