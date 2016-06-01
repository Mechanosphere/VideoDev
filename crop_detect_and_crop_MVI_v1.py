#!/usr/bin/python
import os, sys, subprocess, shlex, re, fnmatch, collections
from subprocess import call
from subprocess import Popen, PIPE
import datetime
from datetime import datetime as dt
import pymysql
from collections import Counter



# GLOBAL DB VARIABLES
conn = pymysql.connect(host='166.77.22.204', port=3306, user='pyuser', passwd='unicornbacon', db='mvi_dev')
cur = conn.cursor()
#cur.execute("SELECT width, height FROM videos Where id=1") # We could inject the latest ID here that is being analyzed? 
CROP_DETECT_LINE = "crop="


# Variables
aspect640x480 = (640, 480)
aspect720x480 = (720, 480)
aspect720x576 = (720, 576)




# Get the local path of the source video from MVI 
def get_localPath():
    last_id = cur.execute('SELECT last_insert_id() FROM videos') #grab the newest ID from MVI DB
    cur.execute("SELECT width, height FROM videos Where id=%s", last_id) # Get height and width of the latest ID
    aspect_ratio = cur.fetchone() # get it as aspect ratio
    print aspect_ratio
    if aspect_ratio == aspect640x480: 
        print "found 640x480 - starting crop detect" 
        cur.execute('SELECT * FROM videos Where id=%s',  last_id)
        details_id = cur.fetchone()
        print details_id
        global localPath
        localPath = details_id[20]
        print localPath
        print "Starting Crop Detect"
        detectCropFile(localPath)
    elif aspect_ratio == aspect720x480:
        print "found 720x480 - starting crop detect"
        cur.execute('SELECT * FROM videos Where id=%s',  last_id)
        details_id = cur.fetchone()
        print details_id
        global localPath
        localPath = details_id[20]
        print localPath
        print "Starting Crop Detect"
        detectCropFile(localPath)
    elif aspect_ratio == aspect720x576:
        print "found 720x576 - starting crop detect" 
        cur.execute('SELECT * FROM videos Where id=%s',  last_id)
        details_id = cur.fetchone()
        print details_id
        global localPath
        localPath = details_id[20]
        print localPath 
        print "Starting Crop Detect"
        detectCropFile(localPath)
    else:
        print "video is not for crop detect" # set stateId to "To Encode"


# GLOBAL FUNCTIONS - crop detect
def detectCropFile(localPath):
    fpath = "/Users/mathiesj/desktop/TwentyonePilots_Tearinmyheart_WEA_France_16F16.mxf"
    print "File to detect crop: %s " % localPath
    global basename
    basename = os.path.basename(localPath)
    print basename
    try:
        p = subprocess.Popen(["ffmpeg", "-i", fpath, "-vf", "cropdetect=24:16:0", "-vframes", "500", "-f", "rawvideo", "-y", "/dev/null"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        infos = p.stderr.read()
        print infos
        allCrops = re.findall(CROP_DETECT_LINE + ".*", infos)
        print allCrops 
        mostCommonCrop = Counter(allCrops).most_common(1)
        print "most common crop: %s" % mostCommonCrop
        print mostCommonCrop[0][0]
        global crop
        crop = mostCommonCrop[0][0]
    except subprocess.CalledProcessError:
        print "crop detect error"
    video_rename() #rename file function
    cropAndEncode(new_file_name)

#Rename video file function 
def video_rename():
    file_path = os.path.dirname(os.path.abspath(localPath))
    global old_file_name
    old_file_name = os.path.abspath(localPath)
    print old_file_name
    bit = "C_"
    newBasename = bit + basename
    print newBasename
    global new_file_name
    new_file_name = file_path + "/" + newBasename
    print new_file_name
    #os.rename(old_file_name, new_file_name) # this will rename the file!! 

 



#Rename video file function 
#def video_rename():
    # save original name as global variable Crop_localPath 
    # then rename video file with "C_" and save as variable 

# Take crop values and crop source video accordingly
def crop_video(new_file_name):
    fpath = "/Users/mathiesj/Desktop/Crop_detect/videos/USUV70901993_640x360_1200.mp4"
    print "File to crop: %s " % new_file_name
    try:
        p = subprocess.Popen(["ffmpeg", "-i", fpath, "-vf", crop, "/Users/mathiesj/Desktop/Crop_detect/videos/Cropped.mp4"], stdout=subprocess.PIPE, stderr=subprocess.PIPE) # change to "old_file_name" for the location of the new file
        infos = p.stderr.read()
        print infos
    except subprocess.CalledProcessError:
        print "crop video error"
    # set video state to "Video Downloaded"


def cropAndEncode(new_file_name):
    fpath = "/Users/mathiesj/desktop/TwentyonePilots_Tearinmyheart_WEA_France_16F16.mxf"
    print "File to detect crop: %s " % fpath
    try:
        p = subprocess.Popen(["ffmpeg", "-i", fpath, "-vf", crop, "-codec:v", "libx264", "-profile:v", "high", "-b:v", "8000k", "-threads", "6", "-pass", "2", "-codec:a", "libfdk_aac", "-b:a", "128K", "-f", "mp4", "/Users/mathiesj/Desktop/Crop_detect/videos/Cropped_h264.mp4"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #infos = p.stderr.read()
        #print infos
        #allSINGLE = re.findall(SINGLE_DETECT_LINE + ".*", infos)
        #allMULTI = re.findall(MULTI_DETECT_LINE + ".*", infos)
        #print "Single = %s and Multi = %s" % (allSINGLE, allMULTI)
        #print allCrops 
        #mostCommonCrop = Counter(allCrops).most_common(1)
        #print "most common crop: %s" % mostCommonCrop
        #print mostCommonCrop[0][0]
        #global crop
        #crop = mostCommonCrop[0][0]
    except subprocess.CalledProcessError:
        print "crop detect error"



# Start 
#get_localPath()
detectCropFile(localPath)







