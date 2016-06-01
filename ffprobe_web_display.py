#!/usr/bin/python
from bottle import route, run
from bottle import template
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


@route('/ffprobe_interlace')
def ffprobe():
	return "ffprobe info: %s" % infos

@route('/ffprobe_frames')
def ffprobe():
    return "ffprobe info: %s" % info

@route('/hello')
def hello():
	return "Hello World"

# GLOBAL FUNCTIONS - PROBE FILE
def detectInterFile():
    fpath = "/Users/mathiesj/desktop/TwentyonePilots_Tearinmyheart_WEA_France_16F16.mxf"
    print "File to detect crop: %s " % fpath
    try:
        p = subprocess.Popen(["ffmpeg", "-filter:v", "idet", "-frames:v", "1000", "-an", "-f", "rawvideo", "-y",  "/dev/null", "-i", fpath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        infos = p.stderr.read()
        global infos
        print infos
        p = subprocess.Popen(["ffprobe", "-select_streams", "v", "-show_frames", fpath, "-print_format", "json",], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        info = p.stdout.read()
        global info
        print info
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
detectInterFile()


run(host='localhost', port=8080, debug=True)



