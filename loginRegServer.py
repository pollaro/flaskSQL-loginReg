from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re,os,md5,binascii
app = Flask(__name__)
app.secret_key = os.urandom(32)
nameRegex = r'^\w{2,}'
nameRegex = re.compile(nameRegex)
emailRegex = r"^\w+@\w+\.[a-z]{3}"
emailRegex = re.compile(emailRegex)
mysql = MySQLConnector(app,'loginReg')


@app.route('/')
def indexPage():
    return render_template('login.html')
@app.route('/register',methods=['POST'])
def register():
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    emailAdd = request.form['emailAdd']
    passWord = request.form['passWord']
    passConf = request.form['passConf']
    print request.form
    error = False
    if not nameRegex.match(firstName):
        flash('First Name may not be empty','firstError')
        error = True
    if not nameRegex.match(lastName):
        flash("Last Name may not be empty",'lastError')
        error = True
    if not emailRegex.match(emailAdd):
        flash("Invalid email address",'emailError')
        error = True
    if len(passWord) < 8:
        flash("Password must be AT LEAST 8 characters",'passShort')
        error = True
    if passWord != passConf:
        flash("Password and Confirm Password must be the same",'passMatch')
        error = True
    if error:
        return redirect('/')
    else:
        salt = binascii.b2a_hex(os.urandom(15))
        hashed_pw = md5.new(passWord + salt).hexdigest()
        query = 'SELECT * FROM users WHERE email = :emailAdd'
        data = {'emailAdd': emailAdd}
        emailCheck = mysql.query_db(query,data)
        print emailCheck
        if not emailCheck:
            query = 'INSERT INTO users (first_name,last_name,email,password,salt,created_at,updated_at) VALUES (:firstName,:lastName,:emailAdd,:passWord,:salt,NOW(),NOW())'
            data = {'firstName':firstName,'lastName':lastName,'emailAdd':emailAdd,'passWord':hashed_pw,'salt':salt}
            mysql.query_db(query,data)
            session['firstName'] = firstName
            session['lastName'] = lastName
            query = 'SELECT * FROM users WHERE email = :emailLog'
            data = {'emailLog':emailAdd}
            loginData = mysql.query_db(query,data)
            session['id'] = loginData[0]['id']
            return render_template('success.html')
        else:
            flash("Email already registered",'emailInUse')
            return redirect('/')
@app.route('/login',methods=['POST'])
def login():
    emailLog = request.form['emailLog']
    passLog = request.form['passLog']
    query = 'SELECT * FROM users WHERE email = :emailLog'
    data = {'emailLog':emailLog}
    loginData = mysql.query_db(query,data)
    print loginData
    if (emailLog == loginData[0]['email'] and md5.new(passLog + loginData[0]['salt']).hexdigest() == loginData[0]['password']):
        session['id'] = loginData[0]['id']
        session['firstName'] = loginData[0]['first_name']
        session['lastName'] = loginData[0]['last_name']
        query = 'INSERT INTO users (updated_at) VALUES (NOW())'
        mysql.query_db(query)
        return render_template('success.html')
    else:
        flash('Email or Pass are not found or do not match in database','loginError')
        return redirect('/')
app.run(debug=True)
