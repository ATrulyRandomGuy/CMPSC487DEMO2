from flask import Flask, request
from flask import *
import sqlite3
from sqlite3 import Error
import os
import simplejson as json
import datetime

app = Flask(__name__)
dbfile = "pythonsqlite.db"  #NAME OF DB FILE

#
#   Various functions that help the below methods
#

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
        return ""
    elif session.get('logged_in') is True:
        return ""
    else:
        session['logged_in'] = False
        session['id'] = -1
        session['username'] = ""
        session['rank'] = ""
        session['returnval'] = ""
    return ""

def isAdmin():
    if session['rank'] == 'Admin':
        return True
    else:
        return False

def isFaculty():
    if session['rank'] == "Faculty":
        return True
    else:
        return False

# checks to see if the user is logged in
def isLoggedIn():
    sessioncreate()
    if session.get('logged_in') is True:
        return True
    else:
        return False

#if user is logged in, will return the file they want
#otherwise, redirects to login page, and will redirect to page they request when done
def requireLogin(returnval):
    if isLoggedIn():
        return app.send_static_file(returnval)
    else:
        session['returnval'] = returnval
        return redirect('/login')

def requireAdminLogin(adminpage, nonadminpage):
    if isLoggedIn():
        if isAdmin():
            return app.send_static_file(adminpage)
        else:
            return app.send_static_file(nonadminpage)
    else:
        session['returnval'] = ""
        return redirect('/login')

#
# STATIC PAGES
#
@app.route('/')
def redirectfromdefaultpage():
    return redirect('/home')

@app.route('/home')
def home():
    return app.send_static_file("default.html")

@app.route('/table')
def table():
    return requireAdminLogin("table_admin.html", "table_user.html")

@app.route('/login')
def login():
    return app.send_static_file("login.html")

@app.route('/booking')
def booking():
    return requireLogin("booking.html")

@app.route('/user/new')
def newUser():
    return app.send_static_file("newuser.html")

#
#   Logout
#

@app.route("/logout")
def logout():
    session['logged_in'] = False
    session['id'] = -1
    session['username'] = ""
    session['rank'] = ""
    return redirect("/")


#
#   Post Methods
#

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

    if data is None:
        flash('wrong password')
        return redirect("/login")

    if data[0] > 0:
        session['logged_in'] = True
        session['id'] = data[0]
        session['username'] = username
        session['rank'] = data[3]
        returnval = session['returnval']
        session['returnval'] = ""
        if returnval is None:
            return redirect('/')
        if returnval is "":
            return redirect('/')
        return app.send_static_file(returnval)
    else:
        flash('wrong password')
        return redirect("/login")


@app.route('/booking', methods=['POST'])
def inputbooking():
    if not isLoggedIn():
        return redirect('/login')
    Name = session.get('id')
    StartDate = request.form['startDate']
    EndDate = request.form['endDate']
    RoomType = request.form['roomType']
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
        return redirect("/booking")
    return redirect("/")


@app.route('/user/new', methods=['POST'])
def inputNewUser():
    Name = request.form['Name']
    Rank = request.form['Rank']
    Password = request.form['Password']
    conn = create_connection(dbfile)
    cur = conn.cursor()
    sql = "INSERT INTO User(name, password, userType) VALUES (?,?,?)"
    task = (Name, Password, Rank)
    try:
        cur.execute(sql, task)
        conn.commit()
    except Error as e:
        print(e)
        return redirect("/user/new")
    finally:
        cur.close()
        conn.close()
    return redirect("/")

#
#   Json routes -> to be changed to be more secure eventually
#

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

@app.route('/json/booking/user/<id>')
def jsonAllReserverationsById(id):
	thisreturnval = []
	conn = create_connection(dbfile)
	cur = conn.cursor()
	sql = "SELECT * FROM Reservations WHERE customerId = " +id
	cur.execute(sql)
	data = cur.fetchall()
	cur.close()
	conn.close()
	for piece in data:
		thisreturnval.append({"id": piece[1],
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



#initilize the controller.py and run the web-server
app.secret_key = os.urandom(12)
app.run(host='localhost', port=8080, debug=True)
