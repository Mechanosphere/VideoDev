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



# GLOBAL FUNCTIONS - PROBE FILE
def ffprobe_frame_file():
    fpath = "/Users/mathiesj/desktop/TwentyonePilots_Tearinmyheart_WEA_France_16F16.mxf"
    print "File to Frame Analyze: %s " % fpath
    try:
        p = subprocess.Popen(["ffprobe", "-select_streams", "v", "-show_frames", fpath, "-print_format", "json",], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        info = p.stdout.read()
        print info
        print type(info)
        for frame_type in info["frames"]:
            print frame_type["pict_type"]
    except subprocess.CalledProcessError:
        print "ffprobe error"

                #posts = db.video_ingest_metadata
                #posts.insert(info)
    #except subprocess.CalledProcessError, e:
        #print "Subprocess Error with file: %s" % file # e.output
    #except ValueError:
        #print "File: has errors" #% fpath 
    #return

# SCRIPT
ffprobe_frame_file()