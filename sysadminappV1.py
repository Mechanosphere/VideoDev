#!/usr/bin/python
import flask
from flask import render_template
from pymongo import MongoClient
from flask import request
import re




app = flask.Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client.storage_db



@app.route('/home')
def home():
    collection = db.dir_collection
    cursor = collection.find({"storage_bucket": re.compile('RT2|RT3')})
    return render_template("listdirs.html", posts=cursor, dir='All Storage')

@app.route('/listdirs')
def get_all_dirs():
    collection = db.dir_collection
    cursor = collection.find({"storage_bucket": re.compile('RT2|RT3')})
    return render_template("listdirs.html", posts=cursor, dir='All Storage')

@app.route('/RT3listdirs')
def get_all_dirsrt3():
    collection = db.dir_collection
    cursor = collection.find({'$and': [
        {"storage_bucket": 'RT3'},
        {"dir_size": re.compile('GB|TB')}]})
    return render_template("listdirs.html", posts=cursor, dir='RT3', size='GB and TB')

@app.route('/RT2listdirs')
def get_all_dirsrt2():
    collection = db.dir_collection
    cursor = collection.find({'$and': [
        {"storage_bucket": 'RT2'},
        {"dir_size": re.compile('GB|TB')}]})
    return render_template("listdirs.html", posts=cursor, dir='RT2', size='GB and TB')

@app.route('/listfilesinpath/<path:dir_path>', methods=['GET'])
def get_all_files(dir_path):
    if request.method == 'GET':
        #app.logger.info("list files was called")
        mod_dir_path = "/" + dir_path
        collection = db.file_collection
        cursor = collection.find({'dir_path': mod_dir_path})
        #cursor = collection.find({'dir_path': re.compile(dir_path)})
        return render_template("listfilesinpath.html", posts=cursor, dir_path=dir_path)



#
# @app.route('/diva')
# def call_diva():
#     r = request.get()
#     return r.text
#
# @app.route('/mediator')
# def call_mediator():
#     r = request.get()
#     return r.text

if __name__ == "__main__":
    #app.run(debug=True, port=5000, threaded=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
