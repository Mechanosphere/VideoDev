from pymongo import MongoClient
from datetime import datetime
import os
import datetime
import os.path
import math



client = MongoClient('mongodb://localhost:27017/')
db = client.archive_db
storage = "/storage_bucket"
dir_path = "/dir_path"

def convert_size(file_size):
   if file_size == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(file_size, 1024)))
   p = math.pow(1024, i)
   s = round(file_size / p, 2)
   return "%s %s" % (s, size_name[i])


def scan_for_file(dir_path, storage_bucket):
    for file in os.listdir(dir_path):
        curpath = os.path.join(dir_path, file)
        if os.path.isfile(curpath):
            if file.startswith('.incomplete'):
                print('found incomplete file:', file)
                archive_filename = os.rename(file, file.replace('.incomplete', ''))
                print(archive_filename)
                file_accessed = datetime.datetime.fromtimestamp(os.path.getatime(curpath))
                file_modified = datetime.datetime.fromtimestamp(os.path.getmtime(curpath))
                file_created = datetime.datetime.fromtimestamp(os.path.getctime(curpath))
                file_size = os.stat(curpath).st_size
                file_convert_size = convert_size(file_size)
                utc_datetime = datetime.datetime.utcnow()
                post = {"storage_bucket": storage_bucket,
                        "dir_path": dir_path,
                        "file_path": curpath,
                        "file_name": archive_filename,
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

        else:
             print('{} dos not match'.format(file))

scan_for_file()


