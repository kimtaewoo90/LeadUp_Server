import sqlite3
from flask import Flask, url_for, render_template, request, redirect, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

import pandas as pd


app = Flask(__name__)
app.secret_key = "234231432423"
app.config['LEADUP_USER_DB'] = 'db/user_db.sqlite3'


@app.route("/")
def home():
    if session.get("logged_in"):
        return render_template('home.html')
    else:
        return render_template('home.html')
    
    
    
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user_id = request.form['user_id']
        user_pw = request.form['user_pw']
        
        conn = sqlite3.connect(app.config["LEADUP_USER_DB"])
        
        user_info = pd.read_sql_query("""SELECT * 
                                            FROM user_info 
                                            WHERE user_id = '{}'""".format(user_id), conn)
        
        if len(user_info) == 0:
            return {"message" : "failed to login",
                    "error" : "not exist user id"}, 500
            
        
        if user_pw != user_info.user_pw[0]:
            return {"message" : "failed to login",
                    "error" : "didn't match password"}, 500
        
        if len(user_info) == 1:
            # check pw
            if user_pw == user_info.user_pw[0]:
                session['username'] = user_info.user_nickname[0]
                session['logged_in'] = True
                
                return jsonify(
                    message = "success",
                    access_token = create_access_token(identify=user_id, elxpires_delta = False)
                )


@app.route("/logout", methods=["POST","GET"])
def logout():
    if request.method == "POST":
        session['logged_in'] = False
        session.pop('username')
        
        return render_template('home.html')
    
    else:
        return render_template('home.html')



@app.route("/register", methods=["POST","GET"])
def register():
    if request.method == "GET":
        return render_template('register.html')
    
    elif request.method == "POST":
        
        user_id = request.form['user_id']
        user_password = request.form['user_password']
        user_email = request.form['user_email']
        user_nickname = request.form['user_nickname']
        user_phone_number = request.form['user_phone_number']
        
        print(request.form)
        
        conn = sqlite3.connect(app.config['LEADUP_USER_DB'])
        
        check_duplicate_phone_number = pd.read_sql_query("""SELECT user_id, user_phone_number 
                                                FROM user_info 
                                                WHERE user_phone_number = '{}'""".format(user_phone_number), conn)
        
        
        check_duplicate_id = pd.read_sql_query("""SELECT user_id, user_phone_number 
                                                FROM user_info 
                                                WHERE user_id = '{}'""".format(user_id), conn)
        
        conn.close()
        
        if len(check_duplicate_phone_number) >= 1:
            return {"message" : "register failed",
                    "error" : "already exist"}, 500
        
        if len(check_duplicate_id) >= 1:
            return {"message" : "register failed",
                    "error" : "duplicated ID"}, 500
        
        
        datas = [user_id, user_password, user_nickname, user_email, user_phone_number]
        conn = sqlite3.connect(app.config['LEADUP_USER_DB'])
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO user_info VALUES (?, ?, ?, ?, ?)
                     """, datas)
        
        conn.commit()
        conn.close()
        
        return {"message" : "success"}, 200
        


if __name__ == "__main__":
    app.run(debug=True)