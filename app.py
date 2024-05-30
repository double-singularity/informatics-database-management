from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.config["SECRET_KEY"] = "12345678"
app.config["SECRET_KEY"] = "12345678"

@app.route("/", methods=["POST", "GET"])
def home():
    return render_template("index.html")