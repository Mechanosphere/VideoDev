import json_parser
import download_media
import video_encoding
from pymongo import MongoClient
import os
import time
import datetime
import subprocess
from subprocess import CalledProcessError
from bson.objectid import ObjectId

client = MongoClient('localhost:27017')
db = client.MediaProcessing


json_url = '/Users/jmathiesen/PycharmProjects/FFMPEG/wavecast_v1/static/json_bank/wavecast_test.json'
dt_stamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')



class WorkFlowControllerStage1:
    def __init__(self):
        self.db = client.MediaProcessing
        self.json_data = json_parser.get_json_data(json_url)
        self.job_key = json_parser.get_job_key(self.json_data)

    def parse_json_data(self):
        print(self.json_data)


    def new_job(self):
        job_key = self.job_key
        media_local_dir = json_parser.generate_media_dir(job_key)
        audio_src_url = json_parser.scrape_audio(self.json_data)
        audio_local_url = download_media.download_audio(audio_src_url, media_local_dir)
        #watermark_src_url = json_parser.scrape_watermark(self.json_data)
        #watermark_local_url = download_media.download_watermark(watermark_src_url, media_local_dir)
        try:
            self.db.JobProcess.update_one({'job_id': job_key},
                                          {'$set':{
                                              "client_name": 'client name',
                                              "title": 'media title',
                                              "job_id": job_key,
                                              "job_status": 'new_job',
                                              "job_status_dtstamp": dt_stamp,
                                              "error": False,
                                              "error_dtstamp": dt_stamp,
                                              "error_notes": 'none',
                                              "ffmpeg_notes": 'TBD',
                                              "author": 'author name',
                                              "short_caption": 'short caption',
                                              "text": ['text paragraph 1', 'text paragraph 2', 'text paragraph 3'],
                                              "source_audio_url": audio_src_url,
                                              "local_audio_ref": audio_local_url,
                                              "final_video_ref": media_local_dir,
                                              "concat_video_ref": media_local_dir,
                                              "watermark_ref": media_local_dir, # update this
                                          }}, upsert=True)

            print('Inserted data successfully')
        except Exception as Error:
            print('data insert error: {}'.format(Error.args))
            self.db.JobProcess.update_one({'job_id': job_key},
                                          {'$set': {
                                              "error": True,
                                              "error_dtstamp": dt_stamp,
                                              "error_notes": Error.args,
                                          }}, upsert=True)


    def add_images_to_id(self):
        get_doc = self.db.JobProcess.find_one({'job_id': self.job_key})
        media_local_dir = get_doc['final_video_ref']
        db_id = get_doc['_id']
        counter = 0
        for element in self.json_data['mappings']:
            for key, val in element.items():
                image_p_no = counter
                counter = counter + 1
                img_src_url = val
                local_img_path = download_media.download_images(img_src_url, media_local_dir)
                download_msg = 'downloading_image_' + str(image_p_no)
                self.db.JobProcess.update_one({'_id': db_id},
                                              {'$set': {
                                                  "job_status": download_msg,
                                                  "job_status_dtstamp": dt_stamp,
                                              }})
                fname = os.path.basename(val)
                image_secs = key
                try:
                    db.JobProcess.update({'_id': db_id},
                                            { '$push': {
                                                'image_details': {
                                                'processed': True,
                                                'position': image_p_no,
                                                'seconds':image_secs,
                                                'src_url':img_src_url,
                                                'image_fname':fname,
                                                'local_url':local_img_path
                                            }
                                            }})
                    print('ID: {} updated successfully'.format(db_id))
                    self.db.JobProcess.update_one({'_id': db_id},
                                                  {'$set': {
                                                      "job_status": 'ready_for_image_encode',
                                                      "job_status_dtstamp": dt_stamp,
                                                  }})
                except Exception as Error:
                    print('data insert error: {}'.format(Error.args))
                    self.db.JobProcess.update_one({'_id': db_id},
                                                  {'$set': {
                                                      "job_status": 'db_insert_error_image_process',
                                                      "job_status_dtstamp": dt_stamp,
                                                      "error": True,
                                                      "error_dtstamp": dt_stamp,
                                                      "error_notes": Error.args,
                                                  }}, upsert=True)


        return print('{}, ID updated'.format(db_id))


class WorkFlowControllerStage2:
    def __init__(self):
        self.db = client.MediaProcessing
        self.FFMPEG_BIN = "ffmpeg"


    def get_all_new_job_ids(self):
        cursor = self.db.JobProcess.find({'job_status': 'ready_for_image_encode'})
        ready_for_image_encode_list = []
        for document in cursor:
            db_id = document['_id']
            ready_for_image_encode_list.append(db_id)
        return ready_for_image_encode_list

    def process_new_jobs(self):
        ready_for_image_encode_list = self.get_all_new_job_ids()
        print(ready_for_image_encode_list)
        for db_id in ready_for_image_encode_list:
            job_id_cursor = self.db.JobProcess.find_one({'_id': db_id})
            job_id = job_id_cursor['job_id']
            cursor = self.db.JobProcess.find({'_id': db_id}).distinct('image_details')
            for item in cursor:
                image_position = item['position']
                image_seconds = item['seconds']
                image_src_url = item['local_url']
                image_fname = item['image_fname']
                image_fname = os.path.splitext(image_fname)[0]
                print('starting encoding of filename: {}, position: {}, seconds:{}, image src url: {}'.format(image_fname, image_position, image_seconds, image_src_url))
                time.sleep(1)
                encode_msg = 'encoding_image_' + image_fname + '_s:' + image_seconds
                self.db.JobProcess.update_one({'_id': db_id},
                                              {'$set': {
                                                  "job_status": encode_msg,
                                                  "job_status_dtstamp": dt_stamp,
                                              }})
                self.ffmpeg_encode(db_id, job_id, image_position, image_seconds, image_src_url, image_fname)

            print('finished encoding job id: {}'.format(job_id))
            encode_msg = 'encode_images_success'
            self.db.JobProcess.update({'_id': db_id},
                                    {'$set': {
                                        'job_status': encode_msg,
                                        "job_status_dtstamp": dt_stamp,
                                    }})


    def ffmpeg_encode(self, db_id, job_id, image_position, image_seconds, image_src_url, image_fname):
        out_dir = '/Users/jmathiesen/PycharmProjects/FFMPEG/wavecast_v1/' + job_id  # location of where the files should go
        out_file = out_dir + '/' + image_fname + '_vid.mp4'  # determining the output video file name and path
        command = [self.FFMPEG_BIN,
                   '-loop', '1', '-f', 'image2',
                   '-i', image_src_url, '-s', '1920x1080', '-c:v', 'libx264',
                   '-t', image_seconds, out_file]
        try:
            ffmpeg_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            for line in ffmpeg_process.stdout:
                print(line)
                self.db.JobProcess.update_one({'_id': db_id},
                                              {'$set': {
                                                  "ffmpeg_notes": line,
                                              }})
            self.db.JobProcess.update({'_id': db_id},
                                         { '$push': {
                                             'video_details': {
                                                'position': image_position,
                                                'local_url': out_file
                                            }
                                         }})
            encode_message = 'ID: {} updated successfully. File: {} encoded successful'.format(db_id, image_fname)
            print(encode_message)
            encode_msg = 'encoding_image_' + image_fname + '_s:' + image_seconds + '_success'
            self.db.JobProcess.update_one({'_id': db_id},
                                          {'$set': {
                                              "job_status": encode_msg,
                                              "job_status_dtstamp": dt_stamp,
                                          }})
            time.sleep(1)
        except Exception as Error:
                print('data insert error: {}'.format(Error.args))
                self.db.JobProcess.update_one({'_id': db_id},
                                              {'$set': {
                                                  "job_status": 'db_insert_error_encode_images',
                                                  "job_status_dtstamp": dt_stamp,
                                                  "error": True,
                                                  "error_dtstamp": dt_stamp,
                                                  "error_notes": Error.args,
                                              }})

##### starting to encode images as a single video

    def get_all_encoded_images_ids(self):
        cursor = self.db.JobProcess.find({'job_status': 'encode_images_success'})
        ready_for_video_encode_id_list = []
        for document in cursor:
            db_id = document['_id']
            ready_for_video_encode_id_list.append(db_id)
        print("list of id for image encode success: {}".format(ready_for_video_encode_id_list))
        return ready_for_video_encode_id_list

    def process_video_list(self):
        video_local_url_list = []
        id_list = self.get_all_encoded_images_ids()
        print(id_list)
        for db_id in id_list:
            job_id_cursor = self.db.JobProcess.find_one({'_id': db_id})
            job_id = job_id_cursor['job_id']
            cursor = self.db.JobProcess.find({'_id': db_id}).distinct('video_details')
            for item in cursor:
                video_local_url_list.append(item['local_url'])
            concat_video_cmd = video_encoding.contruct_concat_cmd(video_local_url_list, job_id, db_id)
            print('ffmpeg cmd for concat; {}'.format(concat_video_cmd))
            self.encode_video(concat_video_cmd, job_id, db_id)


    def encode_video(self, concat_video_cmd, job_id, db_id):
        command = concat_video_cmd
        concat_video = 'concat_video.mp4'
        video_out = '/Users/jmathiesen/PycharmProjects/FFMPEG/wavecast_v1/' + job_id + '/' + concat_video

        try:
            ffmpeg_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            for line in ffmpeg_process.stdout:
                print(line)
                self.db.JobProcess.update_one({'_id': db_id},
                                              {'$set': {
                                                  "ffmpeg_notes": line,
                                                  "job_status": 'encoding_concat_video',
                                                  "job_status_dtstamp": dt_stamp,
                                              }})
            self.db.JobProcess.update({'_id': db_id},
                                      {'$set': {
                                          'job_status': 'encode_videos_success',
                                          'job_status_dtstamp': dt_stamp,
                                          'concat_video_ref': video_out,
                                      }
                                      })
            encode_message = 'ID: {} updated successfully. File: {} encoded successful'.format(db_id, concat_video)
            print(encode_message)
            self.db.JobProcess.update_one({'_id': db_id},
                                          {'$set': {
                                              "job_status": 'encode_concat_video_success',
                                              "job_status_dtstamp": dt_stamp,
                                              "ffmpeg_notes": encode_message,
                                          }})
            time.sleep(1)
        except CalledProcessError as e:
            self.db.JobProcess.update({'_id': db_id},
                                      {'$set': {
                                          'job_status': 'encode_videos_error',
                                          "job_status_dtstamp": dt_stamp,
                                          "error": True,
                                          "error_dtstamp": dt_stamp,
                                          "error_notes": e,
                                      }
                                      })
            print('ID: {} encode error: {}'.format(db_id, e))
            time.sleep(1)

        return ffmpeg_process

##### add audio to cancat video

    def get_all_concat_video_ids(self):
        cursor = self.db.JobProcess.find({'job_status': 'encode_concat_video_success'})
        ready_for_final_video_encode_id_list = []
        for document in cursor:
            db_id = document['_id']
            ready_for_final_video_encode_id_list.append(db_id)
        print("list of id for image encode success: {}".format(ready_for_final_video_encode_id_list))
        return ready_for_final_video_encode_id_list

    def process_concat_video_list(self):
        id_list = self.get_all_concat_video_ids()
        print(id_list)
        for db_id in id_list:
            cursor = self.db.JobProcess.find_one({'_id': db_id})
            job_id = cursor['job_id']
            concat_video_url = cursor['concat_video_ref']
            audio_url = cursor['local_audio_ref']
            add_audio_cmd = video_encoding.contruct_merge_audio_cmd(concat_video_url, audio_url, job_id, db_id)
            print('ffmpeg cmd for add audio; {}'.format(add_audio_cmd))
            self.add_audio(add_audio_cmd, job_id, db_id)

    def add_audio(self, add_audio_cmd, job_id, db_id):
        command = add_audio_cmd
        final_video = 'final_video.mp4'
        video_out = '/Users/jmathiesen/PycharmProjects/FFMPEG/wavecast_v1/' + job_id + '/' + final_video
        try:
            ffmpeg_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            for line in ffmpeg_process.stdout:
                print(line)
                self.db.JobProcess.update_one({'_id': db_id},
                                              {'$set': {
                                                  "ffmpeg_notes": line,
                                                  "job_status": 'encoding_final_video',
                                                  "job_status_dtstamp": dt_stamp,
                                              }})

            encode_message = 'ID: {} updated successfully. File: {} encoded successful'.format(db_id, final_video)
            print(encode_message)
            self.db.JobProcess.update_one({'_id': db_id},
                                          {'$set': {
                                              'job_status': 'encode_final_video_success',
                                              "job_status_dtstamp": dt_stamp,
                                              'final_video_ref': video_out,
                                              "ffmpeg_notes": encode_message,
                                          }})
            time.sleep(1)
        except CalledProcessError as e:
            self.db.JobProcess.update({'_id': db_id},
                                      {'$set': {
                                          'job_status': 'encode_final_video_error',
                                          "job_status_dtstamp": dt_stamp,
                                          "error": True,
                                          "error_dtstamp": dt_stamp,
                                          "error_notes": e,
                                      }
                                      })
            print('ID: {} encode error: {}'.format(db_id, e))
            time.sleep(1)

        return ffmpeg_process



    def add_watermark(self, db_id):
        cursor = self.db.JobProcess.find_one({'_id': ObjectId(db_id)})
        job_id = cursor['job_id']
        wtr_video = 'wtrmark_final.mp4'
        video_out = '/Users/jmathiesen/PycharmProjects/FFMPEG/wavecast_v1/' + job_id + '/' + wtr_video
        src_video_path = cursor['final_video_ref']
        #src_watermark_path = cursor['watermark_ref']
        src_watermark_path = "/Users/jmathiesen/PycharmProjects/FFMPEG/wavecast_v1/9faf4ff8-88b2-4051-bb98-763864ed9206/Wavecastlogo.png"
        command = video_encoding.add_watermarking(src_video_path, src_watermark_path, job_id, db_id)
        print(command)
        try:
            ffmpeg_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            for line in ffmpeg_process.stdout:
                print(line)
                self.db.JobProcess.update_one({'_id': db_id},
                                              {'$set': {
                                                  "ffmpeg_notes": line,
                                                  "job_status": 'encoding_watermark',
                                                  "job_status_dtstamp": dt_stamp,
                                              }})

            encode_message = 'ID: {} updated successfully. File: {} encoded successful'.format(db_id, wtr_video)
            print(encode_message)
            self.db.JobProcess.update_one({'_id': db_id},
                                          {'$set': {
                                              'job_status': 'encode_watermark_success',
                                              "job_status_dtstamp": dt_stamp,
                                              'watermark_video_ref': video_out,
                                              "ffmpeg_notes": encode_message,
                                          }})
            time.sleep(1)
        except CalledProcessError as e:
            self.db.JobProcess.update({'_id': db_id},
                                      {'$set': {
                                          'job_status': 'encode_watermark_error',
                                          "job_status_dtstamp": dt_stamp,
                                          "error": True,
                                          "error_dtstamp": dt_stamp,
                                          "error_notes": e,
                                      }
                                      })
            print('ID: {} encode error: {}'.format(db_id, e))




work_flow = WorkFlowControllerStage1()
work_flow_encode = WorkFlowControllerStage2()
#print(work_flow.new_job())
#print(work_flow.add_images_to_id())
#print(work_flow_encode.process_new_jobs())
#print(work_flow_encode.process_video_list())
#print(work_flow_encode.process_concat_video_list())
##################### watermark testing
#db_id = ObjectId("5bae65856a01f00cd591c35a")
#print(work_flow_encode.add_watermark(db_id))