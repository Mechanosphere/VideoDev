#!/usr/bin/python
import os, sys, subprocess, shlex, re, fnmatch
from subprocess import call
from subprocess import Popen, PIPE
import datetime
from datetime import datetime as dt
import pymongo
from pymongo import MongoClient
import json
from pprint import pprint
import time
import smtplib
from email.mime.text import MIMEText


# GLOBAL VARIABLES
VIDEODROP_DIR="/Users/mathiesj/Desktop/Crop_detect"
FFMPEG_BIN = "ffmpeg"
test_file = "/Users/mathiesj/Desktop/Crop_detect/USIV20000084_640x360_1200.mp4"


#VIDEODROP_DIR="/mnt/VoigtKampff/DTO/DTO_SourceLib"



# GLOBAL FUNCTIONS - PROBE FILE
def detectCrop_file():
    fpath = os.path.join(root, file)
    print fpath
    p = subprocess.Popen(["ffmpeg", "-i", fpath, "-vf", "cropdetect=24:16:0", "dummy.mp4"], stdout=subprocess.PIPE)
    print p.communicate()




# SCRIPT
for root, dirs, files in os.walk(VIDEODROP_DIR):
    for file in files:
        if file.startswith('.'):
            print "file is not ready yet"
        elif file.endswith('.mp4'):
            print "starting Crop Detect"
            print file         
            detectCrop_file()
        else:
            print "no suitable files found"