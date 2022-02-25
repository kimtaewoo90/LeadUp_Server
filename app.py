from flask import Flask, url_for, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['LEADUP_USER_DB'] = '/db/user_db.sqlite3'


@app.route("/")
def home():
    if session.get("logged_in"):
        return render_template('home.html')
    else:
        return render_template('home.html')
    