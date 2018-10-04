from pymongo import MongoClient
import json

client = MongoClient('localhost:27017')
db = client.MediaProcessing

json_url = '/Users/jmathiesen/PycharmProjects/FFMPEG/wavecast_test.json'

def get_json_data(json_url):
    with open(json_url) as data_file:
        json_data = json.loads(data_file.read())
        audio_url = json_data['audio']
        audio_str = str(audio_url)
        split_key = audio_str.replace('/', ' ')
        split_key = split_key.split()
        job_key = split_key[-2]
        #job_key = 'testing1234'
        cursor = db.JobProcess.find({'job_id': job_key }).count()
        if cursor == 0:
            print("New job key found. Returning Json Data starting process.....")
            return json_data
        if cursor > 0:
            (print('Job Key already in database. Returning ID data'))
            cursor = db.JobProcess.find({'job_id': job_key})
            return cursor

get_json_data(json_url)