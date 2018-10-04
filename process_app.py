#!/usr/bin/env python3
import flask
from flask_pymongo import PyMongo
from flask import request
from bson.objectid import ObjectId
from controller import WorkFlowControllerStage2


app = flask.Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/MediaProcessing"
mongo = PyMongo(app)



@app.route('/', methods=['GET', 'POST'])
def index():
    call_db_class = db_calls()
    get_all = call_db_class.get_all_posts()
    return flask.render_template('index.html', items=get_all)

@app.route('/job_data/<db_id>', methods=['GET', 'POST'])
def job_data(db_id):
    call_id_class = IdProcessing(db_id)
    job_data = call_id_class.get_job_data()
    image_details = call_id_class.get_image_details()
    video_details = call_id_class.get_video_details()
    return flask.render_template('JobDataTemplate.html',
                                 jobdata=job_data,
                                 imagedetails=image_details,
                                 videodetails=video_details)

@app.route('/encode_panel/', methods=['GET', 'POST'])
def encode_panel():
    call_db_class = db_calls()
    get_all_wtr_jobs = call_db_class.get_all_watermark_jobs()
    if request.method == 'POST':
        db_id = request.form['_addwatermark']
        print(db_id)
        print('starting watermark encode process')
        work_flow2 = WorkFlowControllerStage2()
        process_watermark = work_flow2.add_watermark(db_id)
        print(process_watermark)
        return "watermarking done"

    return flask.render_template('encode_panel.html', jobsdata=get_all_wtr_jobs)




class db_calls:
    def get_all_posts(self):
        get_posts = mongo.db.JobProcess.find()
        return get_posts

    def get_all_new_jobs(self):
        get_new_jobs = mongo.db.JobProcess.find({'job_status': 'new_job'})
        return get_new_jobs

    def get_all_watermark_jobs(self):
        get_all_wtrmark_jobs = mongo.db.JobProcess.find({'job_status': {'$in': ['encode_final_video_success', 'encode_watermark_success']}})
        return get_all_wtrmark_jobs


    def open_search(self, search_text):
        create_index = mongo.db.info_posts.create_index([('text', 'text')])
        create_index
        get_search = mongo.db.info_posts.find({'$text': {"$search": search_text}}).limit(10)
        result_list = []
        for post in get_search:
            result_list.append(post)
        if not result_list:
            search_none = 'no results'
            return search_none
        else:
            return result_list

class IdProcessing:
    def __init__(self, db_id):
        self.db_id = db_id

    def get_job_data(self):
        job_data = mongo.db.JobProcess.find_one_or_404({'_id': ObjectId(self.db_id)})
        return job_data

    def get_image_details(self):
        image_details = mongo.db.JobProcess.find({'_id': ObjectId(self.db_id)}).distinct('image_details')
        return image_details

    def get_video_details(self):
        video_details = mongo.db.JobProcess.find({'_id': ObjectId(self.db_id)}).distinct('video_details')
        return video_details

    def get_ffmpeg_cmds(self):
        ffmpeg_cmd = mongo.db.JobProcess.find({'_id': ObjectId(self.db_id)}).distinct('ffmpeg_cmds')
        return ffmpeg_cmd

if __name__=='__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)

