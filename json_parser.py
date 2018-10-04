import urllib.request
import os
import json
from pymongo import MongoClient
import time

client = MongoClient('localhost:27017')
db = client.MediaProcessing

def get_json_data(json_url):
    with open(json_url) as data_file:
        parsed_json = json.loads(data_file.read())
    return parsed_json

def get_job_key(json_data):
    audio_url = json_data['audio']
    audio_str = str(audio_url)
    split_key = audio_str.replace('/', ' ')
    split_key = split_key.split()
    job_key = split_key[-2]
    return job_key

def generate_media_dir(job_key):
    get_job_uuid = job_key
    media_path = '/Users/jmathiesen/PycharmProjects/FFMPEG/wavecast_v1/' + get_job_uuid + '/'
    if not os.path.exists(media_path):
        print('dir: {} does not exit.'.format(media_path, media_path))
        os.mkdir(media_path)
        print('Dir: {} has now been created'.format(media_path))
        time.sleep(1)
        return media_path
    elif os.path.exists(media_path):
        print('{} dir already exists'.format(media_path))
        return media_path
    else:
        print('Dir error')
        dir_error = "dir_mk_error"
        return dir_error

def scrape_images(json_data):
    image_items_list = []
    for element in json_data['mappings']:
        for key, val in element.items():
            image_items_list.append(val)
    return image_items_list

def scrape_audio(json_data):
    source_audio_url = json_data['audio']
    return source_audio_url

def scrape_watermark(json_data):
    source_watermark_url = json_data['watermark'] # needs updating
    return source_watermark_url