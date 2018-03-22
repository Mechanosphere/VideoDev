import os
import math
from os.path import join, getsize
import json
from pymongo import MongoClient
import datetime


client = MongoClient('mongodb://localhost:27017/')
db = client.storage_db


#src_dir = "/Users/jonathanmathiesen/Documents/TEST"
src_dir = "/home/ecgmo/rt3"
dirs_dict = {}


def convert_size(total_size):
   if total_size == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(total_size, 1024)))
   p = math.pow(1024, i)
   s = round(total_size / p, 2)
   return "%s %s" % (s, size_name[i])

def check_db_for_symlink(root):
    collection = db.dir_collection
    if collection.find({'dir_path': root}).count() > 0:
        print('found dir in db', root)
        cursor = collection.find({'dir_path': root})
        for document in cursor:
            dir_db_id = document['_id']
            utc_datetime = datetime.datetime.utcnow()
            update_id = collection.update_one(
                {'_id': dir_db_id},
                {
                    "$set": {
                        "error": 0,
                        "is_symlink": True,
                        "permission": True,
                        "dir_size": 0,
                        "process_datestamp": utc_datetime.strftime("%Y-%m-%d %H:%M:%S")
                    },
                },
                upsert=True)
            update_id
            print('Updated ID:', dir_db_id)
    elif collection.find({'dir_path': root}).count() > 0:
        utc_datetime = datetime.datetime.utcnow()
        post = {"storage_bucket": "RT3",
                "dir_path": root,
                "error": 0,
                "is_symlink": True,
                "permission": True,
                "process_datestamp": utc_datetime.strftime("%Y-%m-%d %H:%M:%S")}
        posts = db.dir_collection
        post_id = posts.insert_one(post).inserted_id
        post_id
        print('posted ID:', post)






def check_db_for_dir(root, files, dirs):
    collection = db.dir_collection
    if collection.find({'dir_path': root}).count() > 0:
        print('found dir in db', root)
        cursor = collection.find({'dir_path': root})
        for document in cursor:
            dir_db_id = document['_id']
            size = sum(getsize(join(root, name)) for name in files)
            subdir_size = sum(dirs_dict[join(root, d)] for d in dirs)
            total_size = dirs_dict[root] = size + subdir_size
            dir_total_size = convert_size(total_size)
            dir_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(root))
            dir_ctime = datetime.datetime.fromtimestamp(os.path.getctime(root))
            utc_datetime = datetime.datetime.utcnow()
            update_id = collection.update_one(
                {'_id': dir_db_id},
                {
                    "$set": {
                        "dir_ctime": dir_ctime,
                        "dir_mtime": dir_mtime,
                        "error": 0,
                        "is_symlink": True,
                        "permission": True,
                        "dir_size": dir_total_size,
                        "process_datestamp": utc_datetime.strftime("%Y-%m-%d %H:%M:%S")
                    }
                },
                upsert=True)
            update_id
            print('ID processed:', dir_db_id)
    elif collection.find({'dir_path': root}).count() == 0:
        try:
            size = sum(getsize(join(root, name)) for name in files)
            subdir_size = sum(dirs_dict[join(root, d)] for d in dirs)
            total_size = dirs_dict[root] = size + subdir_size
            dir_total_size = convert_size(total_size)
            utc_datetime = datetime.datetime.utcnow()
            dir_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(root))
            dir_ctime = datetime.datetime.fromtimestamp(os.path.getctime(root))
            post = {"storage_bucket": "RT3",
                    "dir_path": root,
                    "dir_ctime": dir_ctime,
                    "dir_mtime": dir_mtime,
                    "error": 0,
                    "is_symlink": False,
                    "permission": True,
                    "dir_size": dir_total_size,
                    "process_datestamp": utc_datetime.strftime("%Y-%m-%d %H:%M:%S")}
            posts = db.dir_collection
            post_id = posts.insert_one(post).inserted_id
            post_id
            print('posted ID:', post)
        except KeyError:
            print("KeyError", root)
            utc_datetime = datetime.datetime.utcnow()
            post = {"storage_bucket": "RT3",
                    "dir_path": root,
                    "error": 1,
                    "is_symlink": False,
                    "permission": False,
                    "dir_size": 0,
                    "process_datestamp": utc_datetime.strftime("%Y-%m-%d %H:%M:%S")}
            posts = db.dir_collection
            post_id = posts.insert_one(post).inserted_id
            post_id
            print('posted ID:', post)
            #continue
        except OSError:
            print("OSError", root)
            utc_datetime = datetime.datetime.utcnow()
            post = {"storage_bucket": "RT3",
                    "dir_path": root, "error": 1,
                    "is_symlink": False,
                    "permission": False,
                    "dir_size": 0,
                    "process_datestamp": utc_datetime.strftime("%Y-%m-%d %H:%M:%S")}
            posts = db.dir_collection
            post_id = posts.insert_one(post).inserted_id
            post_id
            print('posted ID:', post)
            #continue
    else:
        print("error")
        raise Exception("error", root)
        #continue








def dir_walker2(src_dir):
    try:
        for root, dirs, files in os.walk(src_dir, topdown = False):
            if os.path.islink(root):
                check_db_for_symlink(root)
            elif os.path.isdir(root):
                check_db_for_dir(root, files, dirs)
    except KeyError:
        print("KeyError", root)
        utc_datetime = datetime.datetime.utcnow()
        post = {"storage_bucket": "RT3",
                "dir_path": root,
                "error": "KeyError",
                "is_symlink": False,
                "permission": False,
                "dir_size": 0,
                "process_datestamp": utc_datetime.strftime("%Y-%m-%d %H:%M:%S")}
        posts = db.dir_collection
        post_id = posts.insert_one(post).inserted_id
        post_id
        print('posted ID:', post)
        pass

    except PermissionError as e:
        utc_datetime = datetime.datetime.utcnow()
        post = {"storage_bucket": "RT2",
                "dir_path": root,
                "is_symlink": False,
                "permission": False,
                "dir_size": 0,
                "process_datestamp": utc_datetime.strftime("%Y-%m-%d %H:%M:%S")}
        posts = db.dir_collection
        post_id = posts.insert_one(post).inserted_id
        post_id
        print('posted ID:', post)


dir_walker2(src_dir)