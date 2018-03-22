#!/usr/bin/python
import flask
from flask import render_template
from flask import request
from pymongo import MongoClient
from flask import request
import re




app = flask.Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client.archive_db



@app.route('/divafile/<archive_filename>')
def divafile(archive_filename):
    collection = db.dir_collection
    cursor = collection.find({"file_name": re.compile('RT2|RT3')})
    return render_template("listdirs.html", posts=cursor, dir='All Storage')





#
@app.route('/diva/filename/<archive_filename')
def call_diva():
    r = request.get()
    return r.text
#
# @app.route('/mediator')
# def call_mediator():
#     r = request.get()
#     return r.text
#     return r.json


if __name__ == "__main__":
    #app.run(debug=True, port=5000, threaded=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
