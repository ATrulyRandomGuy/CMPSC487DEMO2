from flask import Flask, request
from flask import *
import sqlite3
from sqlite3 import Error
#from sqlalchemy import *
#from sqlalchemy.orm import sessionmaker
#from tabledef import *
import os
import simplejson as json
import datetime

#engine = create_engine('sqlite:///pythonsqlite.db', echo = True)
app = Flask(__name__)

#Session = sessionmaker(bind=engine)
#s = Session()

dbfile = "pythonsqlite.db"  #NAME OF DB FILE
def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn

#This will initilize the session cookie with values that are logged in
def sessioncreate():
    if session.get('logged_in') is False:
        print(session)
        return ""
    elif session.get('logged_in') is True:
        print(session)
        return ""
    else:
        session['logged_in'] = False
        session['id'] = -1
        session['username'] = ""
        session['rank'] = ""
        print(session)
    return ""

@app.route('/')
def home():
    sessioncreate()
    return app.send_static_file("default.html")

@app.route('/table')
def table():
    sessioncreate()
    if session.get('logged_in') == False:
        return redirect("login")
    else:
        return app.send_static_file("table.html")

@app.route('/login')
def login():
    sessioncreate()
    return app.send_static_file("login.html")

@app.route('/login', methods=['POST'])
def dologin():
    username = request.form['username']
    password = request.form['password']

    conn = create_connection(dbfile)
    cur = conn.cursor()
    sql = "Select * from User where name is '" + username + "' and password is '" + password +"'"
    cur.execute(sql)
    data = cur.fetchone()
    cur.close()
    conn.close()

    if data[0] > 0:
        session['logged_in'] = True
        session['id'] = data[0]
        session['username'] = username
        session['rank'] = data[3]
        return redirect("/table")
    else:
        flash('wrong password')
        return redirect("/login")

@app.route("/logout")
def logout():
    session['logged_in'] = False
    session['id'] = -1
    session['username'] = ""
    session['rank'] = ""
    return redirect("/")

@app.route("/session")
def testroute():
    print(session)
    return ""

@app.route('/json/users')
def getAllUsers():
    returnval = []
    conn = create_connection(dbfile)
    cur = conn.cursor()
    sql = "Select * from User"
    cur.execute(sql)
    data = cur.fetchall()
    cur.close()
    conn.close()
    for user in data:
        returnval.append({"id": user[0],
                        "name": user[1],
                        "password": user[2],
                        "userType": user[3]})
    return json.dumps(returnval)

@app.route('/json/user/<id>')
def getUserById(id):
    conn = create_connection(dbfile)
    cur = conn.cursor()
    sql = "Select * from User where id = " + id
    cur.execute(sql)
    data = cur.fetchone()
    cur.close()
    conn.close()
    returnval = {"id": data[0],
                    "name": data[1],
                    "password": data[2],
                    "userType": data[3]}
    return json.dumps(returnval)


@app.route('/user/new')
def newUser():
    return app.send_static_file("newuser.html")

@app.route('/user/new', methods=['POST'])
def inputNewUser():
    Name = request.forms.get('Name')
    Rank = request.forms.get('Rank')
    Password = request.forms.get('Password')
    conn = create_connection(dbfile)
    cur = conn.cursor()
    sql = "INSERT INTO User(name, password, userType) VALUES (?,?,?)"
    task = (Name, Password, Rank)
    try:
        cur.execute(sql, task)
        conn.commit()
    except Error as e:
        print(e)
        redirect("/user/new")
    finally:
        cur.close()
        conn.close()
    redirect("/")

@app.route('/booking')
def booking():
    return app.send_static_file("booking.html")

@app.route('/booking', methods=['POST'])
def inputbooking():
    Name = request.forms.get('name')
    StartDate = request.forms.get('startDate')
    EndDate = request.forms.get('endDate')
    RoomType = request.forms.get('roomType')
    conn = create_connection(dbfile)
    cur = conn.cursor()
    sql = "INSERT INTO Reservations(customerId, startDate, endDate, roomType) VALUES (?,?,?,?)"
    task = (Name, StartDate, EndDate, RoomType)
    try:
        cur.execute(sql, task)
        conn.commit()
    except Error as e:
        cur.close()
        conn.close()
        print(e)
        redirect("/booking")
    redirect("/")

@app.route('/json/booking')
def jsonAllReservations():
    thisreturnval = []
    conn = create_connection(dbfile)
    cur = conn.cursor()
    sql = "Select * from Reservations"
    cur.execute(sql)
    data = cur.fetchall()
    cur.close()
    conn.close()
    for piece in data:
        #customer = json.loads(getUserById(str(piece[0])))
        thisreturnval.append({"id": piece[0],
                        "customerId": piece[1],
                        "startDate": piece[2],
                        "endDate": piece[3],
                        "roomType": piece[4]})
    return json.dumps(thisreturnval)

@app.route('/json/booking/future')
def jsonReservationsFuture():
    now = datetime.datetime.now()
    thisreturnval = []
    print(now)
    conn = create_connection(dbfile)
    cur = conn.cursor()
    sql = "Select * from Reservations where startDate > DateTime('"+str(now.year) + "-" + str(now.month) +"-"+str(now.day) + " 00:00:00"+"');"
    cur.execute(sql)
    data = cur.fetchall()
    cur.close()
    conn.close()
    for piece in data:
        #customer = json.loads(getUserById(str(piece[0])))
        thisreturnval.append({"id": piece[0],
                        "customerId": piece[1],
                        "startDate": piece[2],
                        "endDate": piece[3],
                        "roomType": piece[4]})
    return json.dumps(thisreturnval)

@app.route('/json/booking/current')
def jsonReservationsCurrent():
    now = datetime.datetime.now()
    thisreturnval = []
    print(now)
    conn = create_connection(dbfile)
    cur = conn.cursor()
    sql = "Select * from Reservations where startDate <= DateTime('"+str(now.year) + "-" + str(now.month) +"-"+str(now.day) + " 00:00:00"+"') and endDate >= DateTime('"+str(now.year) + "-" + str(now.month) +"-"+str(now.day) + " 00:00:00"+"');"
    cur.execute(sql)
    data = cur.fetchall()
    cur.close()
    conn.close()
    for piece in data:
        #customer = json.loads(getUserById(str(piece[0])))
        thisreturnval.append({"id": piece[0],
                        "customerId": piece[1],
                        "startDate": piece[2],
                        "endDate": piece[3],
                        "roomType": piece[4]})
    return json.dumps(thisreturnval)

@app.route('/json/booking/past')
def jsonReservationsPast():
    now = datetime.datetime.now()
    thisreturnval = []
    print(now)
    conn = create_connection(dbfile)
    cur = conn.cursor()
    sql = "Select * from Reservations where endDate < DateTime('"+str(now.year) + "-" + str(now.month) +"-"+str(now.day) + " 00:00:00"+"');"
    cur.execute(sql)
    data = cur.fetchall()
    cur.close()
    conn.close()
    for piece in data:
        #customer = json.loads(getUserById(str(piece[0])))
        thisreturnval.append({"id": piece[0],
                        "customerId": piece[1],
                        "startDate": piece[2],
                        "endDate": piece[3],
                        "roomType": piece[4]})
    return json.dumps(thisreturnval)

@app.route('/register')
def signup():
    if user is not "":
        return redirect("/table")
    else:
        redirect("/login")

@app.route('/register', methods=['POST'])
def inputhome():
    if user is not "":
            Fname = request.forms.get('Fname')
            Lname = request.forms.get('Lname')
            Email = request.forms.get('Email')


app.secret_key = os.urandom(12)
app.run(host='localhost', port=8080, debug=True)
