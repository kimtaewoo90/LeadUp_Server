import sqlite3
from flask import Flask, url_for, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy

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
            flash("존재하지 않는 유저입니다. 가입을 부탁드립니다.")
            return render_template('home.html')
        
        elif len(user_info) == 1:
            # check pw
            if user_pw == user_info.user_pw[0]:
                session['username'] = user_info.user_nickname[0]
                session['logged_in'] = True
                
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
        
        # 동일인 여러번 가입 방지
        check_duplicate_phone_number = pd.read_sql_query("""SELECT user_id, user_phone_number 
                                                FROM user_info 
                                                WHERE user_phone_number = '{}'""".format(user_phone_number), conn)
        
        
        # 같은 아이디 사용 방지
        check_duplicate_id = pd.read_sql_query("""SELECT user_id, user_phone_number 
                                                FROM user_info 
                                                WHERE user_id = '{}'""".format(user_id), conn)
        
        conn.close()
        
        if len(check_duplicate_phone_number) >= 1:
            flash("LeadUp 원칙상 1인1계정이 원칙입니다.")
            return render_template('register.html')
        
        if len(check_duplicate_id) >= 1:
            flash("아이디가 중복됩니다. 다시 시도해주세요.")
            return render_template('register.html')
        
        
        # 회원가입 절차
        datas = [user_id, user_password, user_nickname, user_email, user_phone_number]
        conn = sqlite3.connect(app.config['LEADUP_USER_DB'])
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO user_info VALUES (?, ?, ?, ?, ?)
                     """, datas)
        
        conn.commit()
        conn.close()
        
        flash("가입이 완료되었습니다.")
        return render_template('register.html')




if __name__ == "__main__":
    app.run(debug=True)