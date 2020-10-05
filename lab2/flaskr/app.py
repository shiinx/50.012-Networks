# Randomly thought API service to fulfill lab objectives
# Service: Random string generator and storage service
# Uses sqlite3 for database
# Ensure lab2.db is in the same directory as lab2.py
# run client.sh to see demo of API

import random
import sqlite3
import string

from flask import Flask
from flask import request

app = Flask(__name__)


# Index page to list possible url combinations
@app.route('/', methods=['GET'])
def index():
    return {
               '/create': 'To create a new random string, POST only',
               '/strings': 'List all stored strings, GET only',
               '/strings/<uid>': 'Returns selected string, GET only',
               '/admin/strings/<uid>': 'Admin method for selected string, GET/PUT/DELETE'
           }, 200


# To create a random string with user posted settings
# Stores in sqlite3 database file lab2.db
@app.route('/create', methods=['POST'])
def create():
    data = request.get_json()

    length = data['length']
    allowUpperCase = data['allowUpperCase']
    allowDigits = data['allowDigits']
    allowSpecialCharacters = data['allowSpecialCharacters']

    randString = getRandomString(length, allowUpperCase, allowDigits, allowSpecialCharacters)

    conn = sqlite3.connect('lab2.db')
    cur = conn.cursor()
    cur.execute('INSERT INTO strings(string) VALUES(?);', (randString,))
    conn.commit()
    conn.close()

    return {'status': 'successfully created random string: ' + randString}, 201


# To return a dictionary/json of the stored strings with ids
@app.route('/strings', methods=['GET'])
def strings():
    conn = sqlite3.connect('lab2.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM strings')
    allStrings = cur.fetchall()
    conn.close()
    return dict(allStrings), 200


# To return a dictionary/json of specific stored string with specified uid
@app.route('/strings/<uid>', methods=['GET'])
def get(uid):
    conn = sqlite3.connect('lab2.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM strings WHERE uid = ?', (uid,))
    d = cur.fetchone()
    if d is None:
        return {'status': '404 error'}, 404

    conn.close()
    return {d[0]: d[1]}, 200


# Admin method to get, manually input/change and delete string
# Requires login, user = admin, password = password
# PUT supports both application/json and text/plain
@app.route('/admin/strings/<uid>', methods=['GET', 'PUT', 'DELETE'])
def admin(uid):
    if not isAuthorized(request.authorization):
        return {'status': '401 error'}, 401

    conn = sqlite3.connect('lab2.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM strings WHERE uid = ?', (uid,))
    row = cur.fetchone()

    if request.method == 'GET':
        if row is None:
            msg = {'status': '404 error'}, 404
        else:
            msg = {row[0]: row[1]}, 200
    elif request.method == 'PUT':
        newString = ''
        if request.mimetype == 'application/json':
            data = request.get_json()
            newString = data['newString']
        elif request.mimetype == 'text/plain':
            newString = request.get_data(as_text=True)
        if row is None:
            cur.execute('INSERT INTO strings(uid, string) VALUES(?,?);', (uid, newString,))
            msg = {'status': 'successfully created'}, 201
        else:
            cur.execute('UPDATE strings SET string = ? WHERE uid = ?;', (newString, uid,))
            msg = {'status': 'successfully updated'}, 200
    else:
        if row is None:
            msg = {'status': '404 error'}, 404
        else:
            cur.execute('DELETE FROM strings WHERE uid = ?', (uid,))
            msg = {'status': 'successfully deleted'}, 204

    conn.commit()
    conn.close()
    return msg


# function to get random string
def getRandomString(length, allowUpperCase, allowDigits, allowSpecialCharacters):
    pool = string.ascii_lowercase

    if allowUpperCase:
        pool += string.ascii_uppercase
    if allowDigits:
        pool += string.digits
    if allowSpecialCharacters:
        pool += string.punctuation

    return ''.join(random.choice(pool) for i in range(length))


# function to check user authorization
def isAuthorized(auth):
    if auth is None or not (auth.username == 'admin' and auth.password == 'password'):
        return False
    return True


if __name__ == '__main__':
    app.run(debug=True)
