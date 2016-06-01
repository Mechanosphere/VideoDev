#!/usr/bin/python
import os, sys, subprocess, shlex, re, fnmatch, collections
from subprocess import call
from subprocess import Popen, PIPE
import datetime
from datetime import datetime as dt
from collections import Counter
from bottle import route, run 




# GLOBAL VARIABLES
movfpath = "/Users/mathiesj/desktop/mov_proxy_test.mov"
mp4fpath = "/Users/mathiesj/desktop" + "/" + "rewrap2MP4_v2.mp4"



# GLOBAL FUNCTIONS - interlace detect
def rewrapvideo():
    print "mov video file to rewrap: %s " % movfpath
    try:
        p = subprocess.Popen(["ffmpeg", "-i", movfpath, "-vcodec", "copy", "-acodec", "copy", mp4fpath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        info = p.stderr.read()
        print info
    except subprocess.CalledProcessError:
        print "ffmpeg rewrap error"

def ffprobe_mov():
    print "mov video file probe: %s" % movfpath
    try:
        p = subprocess.Popen(["ffprobe", "-show_format", "-show_streams", movfpath, "-print_format", "json",], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        global movinfo
        movinfo = p.stdout.read()
        print movinfo
    except subprocess.CalledProcessError:
        print "ffprobe error"

def ffprobe_mp4():
    print "mp4 video file probe: %s" % mp4fpath
    try:
        p = subprocess.Popen(["ffprobe", "-show_format", "-show_streams", mp4fpath, "-print_format", "json",], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        global mp4info
        mp4info = p.stdout.read()
        print mp4info
    except subprocess.CalledProcessError:
        print "ffprobe error"

# Start
ffprobe_mov() 
rewrapvideo()
ffprobe_mp4()

@route('/rewrap')
def ffprobe_info():
    return "This is the .mov ffprobe: %s and this is the .mp4 ffprobe: %s " % (movinfo, mp4info) 
    return mp4info




run(host='localhost', port=8080, debug=True)
