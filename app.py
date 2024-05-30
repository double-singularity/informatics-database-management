from flask import Flask, render_template, request, session, redirect, url_for
from db import Database

app = Flask(__name__)
app.config["SECRET_KEY"] = "12345678"


@app.route("/", methods=["POST", "GET"])
def home():
    return render_template("index.html")

test = Database()

@app.route("/display", methods=["POST", "GET"])
def display():
    return render_template("display.html", my_list=test.exec("SELECT * FROM mahasiswa"))