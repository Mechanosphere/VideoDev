#!/usr/bin/env python3
import flask
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from controller import WorkFlowControllerStage2


app = flask.Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/MediaProcessing"
mongo = PyMongo(app)

@app.route('/json')
def json():
    return flask.render_template('admin_panel.html')


@app.route('/image_download')
def image_download():
    print('hello')
    return "nothing"

@app.route('/transcode_images')
def transcode_images():
    print('hello')
    work_flow2 = WorkFlowControllerStage2()
    process_new = work_flow2.process_new_jobs()
    print(process_new)
    return "nothing"

