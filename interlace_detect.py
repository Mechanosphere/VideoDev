#!/usr/bin/python
import os, sys, subprocess, shlex, re, fnmatch, collections
from subprocess import call
from subprocess import Popen, PIPE
import datetime
from datetime import datetime as dt
import pymysql
from collections import Counter



# GLOBAL VARIABLES
SINGLE_DETECT_LINE = "Single frame detection: TFF:"
MULTI_DETECT_LINE = "Multi frame detection: TFF:"



# GLOBAL FUNCTIONS - interlace detect
def detectInterFile():
    fpath = "/Users/mathiesj/desktop/TwentyonePilots_Tearinmyheart_WEA_France_16F16.mxf"
    print "File to detect crop: %s " % fpath
    try:
        p = subprocess.Popen(["ffmpeg", "-filter:v", "idet", "-frames:v", "1000", "-an", "-f", "rawvideo", "-y",  "/dev/null", "-i", fpath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        infos = p.stderr.read()
        print infos
        allSINGLE = re.findall(SINGLE_DETECT_LINE + ".*", infos)
        allMULTI = re.findall(MULTI_DETECT_LINE + ".*", infos)
        print "Single = %s and Multi = %s" % (allSINGLE, allMULTI)
        #print allCrops 
        #mostCommonCrop = Counter(allCrops).most_common(1)
        #print "most common crop: %s" % mostCommonCrop
        #print mostCommonCrop[0][0]
        #global crop
        #crop = mostCommonCrop[0][0]
    except subprocess.CalledProcessError:
        print "crop detect error"


def cropAndEncode():
    fpath = "/Users/mathiesj/desktop/TwentyonePilots_Tearinmyheart_WEA_France_16F16.mxf"
    print "File to detect crop: %s " % fpath
    try:
        p = subprocess.Popen([["ffmpeg", "-i", fpath, "-vf", crop, "-codec:v", "libx264", "-profile:v", "high", "-b:v", "8000k", "-threads", "6", "-pass", "2", "-codec:a", "libfdk_aac", "-b:a", "128K", "-f", "mp4", "/Users/mathiesj/Desktop/Crop_detect/videos/Cropped_h264.mp4"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
cropAndEncode()