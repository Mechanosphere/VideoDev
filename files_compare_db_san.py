import pymongo
import json
from pymongo import MongoClient
from datetime import datetime
import os
import datetime
import os.path
import re
import math



client = MongoClient('mongodb://localhost:27017/')
db = client.storage_db


def convert_size(file_size):
   if file_size == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(file_size, 1024)))
   p = math.pow(1024, i)
   s = round(file_size / p, 2)
   return "%s %s" % (s, size_name[i])




def find_and_scan_files():
    collection = db.file_collection
    cursor = collection.find()
    for document in cursor:
        file_path = document['file_path']
        file_id = document['_id']
        if os.path.isfile(file_path):
            print('file is:', file_path)
            file_accessed = datetime.datetime.fromtimestamp(os.path.getatime(file_path))
            file_modified = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            file_created = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
            file_size = os.stat(file_path).st_size
            file_convert_size = convert_size(file_size)
            utc_datetime = datetime.datetime.utcnow()
            update_id = collection.update_one(
                {'_id': file_id},
                {
                    "$set": {
                        "file_size": file_convert_size,
                        "file_size_bytes": file_size,
                        "process_datestamp": utc_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                        "file_created": file_created,
                        "file_accessed": file_accessed,
                        "file_modified": file_modified
                    },
                },
                upsert=True)
            update_id
        else:
            print('file is not available:', file_path)
            delete_id = collection.delete_one(file_id)
            delete_id


def scan_for_file(dir_path, storage_bucket):
    for file in os.listdir(dir_path):
        curpath = os.path.join(dir_path, file)
        if os.path.isfile(curpath):
            print('found file:', file)
            print('checking db for:', curpath)
            collection = db.file_collection
            if collection.find({'file_path': curpath}).count() > 0:
                print('found file in db', curpath)
                cursor = collection.find({'file_path': curpath})
                for document in cursor:
                    file_db_id = document['_id']
                    file_db_path = document['file_path']
                    file_accessed = datetime.datetime.fromtimestamp(os.path.getatime(file_db_path))
                    file_modified = datetime.datetime.fromtimestamp(os.path.getmtime(file_db_path))
                    file_created = datetime.datetime.fromtimestamp(os.path.getctime(file_db_path))
                    file_size = os.stat(file_db_path).st_size
                    file_convert_size = convert_size(file_size)
                    utc_datetime = datetime.datetime.utcnow()
                    update_id = collection.update_one(
                        {'_id': file_db_id},
                        {
                            "$set": {
                                "file_size": file_convert_size,
                                "file_size_bytes": file_size,
                                "process_datestamp": utc_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                                "file_created": file_created,
                                "file_accessed": file_accessed,
                                "file_modified": file_modified
                            },
                        },
                        upsert=True)
                    update_id
                    print('Updated ID:', file_db_id)

            elif collection.find({'file_path': curpath}).count() == 0:
                print('no file in db:', curpath)
                file_accessed = datetime.datetime.fromtimestamp(os.path.getatime(curpath))
                file_modified = datetime.datetime.fromtimestamp(os.path.getmtime(curpath))
                file_created = datetime.datetime.fromtimestamp(os.path.getctime(curpath))
                file_size = os.stat(curpath).st_size
                file_convert_size = convert_size(file_size)
                utc_datetime = datetime.datetime.utcnow()
                post = {"storage_bucket": storage_bucket,
                        "dir_path": dir_path,
                        "file_path": curpath,
                        "file_name": file,
                        "file_size": file_convert_size,
                        "file_size_bytes": file_size,
                        "process_datestamp": utc_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                        "file_created": file_created,
                        "file_accessed": file_accessed,
                        "file_modified": file_modified}
                posts = db.file_collection
                post_id = posts.insert_one(post).inserted_id
                post_id
                print('New posted ID:', post)
            else:
                print('error')





def scan_storagebuckets():
    collection = db.dir_collection
    cursor = collection.find({"dir_size": re.compile('KB|MB|GB|TB')})

    for document in cursor:
        storage = document["storage_bucket"]
        dir_path = document["dir_path"]
        if storage == "RT2":
            print('searching RT2 path:', dir_path)
            storage_bucket = "RT2"
            scan_for_file(dir_path, storage_bucket)
        elif storage == "RT3":
            print('searching RT3 path:', dir_path)
            storage_bucket = "RT3"
            scan_for_file(dir_path, storage_bucket)
        elif storage == "RT4":
            print('searching RT4 path:', dir_path)
            storage_bucket = "RT4"
            scan_for_file(dir_path, storage_bucket)





scan_storagebuckets()
