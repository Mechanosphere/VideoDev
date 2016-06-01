#!/usr/bin/python
import os, sys, subprocess, shlex, re, fnmatch
import shutil
import time
import xml.etree.ElementTree as ET
import datetime
import json
import uuid
from subprocess import call
from subprocess import Popen, PIPE
from pprint import pprint
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
# from mariaaws_class_sql_v1 import *
from config import *








# GLOBAL FUNCTIONS - PROBE FILE
def ffprobefile(fpath):
    print "File to ffprobe analyze: %s " % fpath
    try:
        p = subprocess.Popen(["ffprobe", "-v", "quiet", "-show_format", "-show_streams", "-print_format", "json", fpath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        info = p.communicate()[0] # p.stdout.read()
        print info 
        global parsed_json
        parsed_json = json.loads(info)
        parseJson(parsed_json)
    except subprocess.CalledProcessError:
        print "ffprobe error"
        create_date = datetime.datetime.utcnow()
        asset_path = fpath
        fname = os.path.basename(fpath)
        filename = fname
        ffprobe_error = "ffprob error" 
        nb_streams = ffprobe_error
        format_name = ffprobe_error
        format_long_name = ffprobe_error 
        video_duration = ffprobe_error 
        bit_rate = ffprobe_error
        encoding_media_id = ffprobe_error 
        sys_isrc = ffprobe_error
        new_format_object = FormatMetadata(31, create_date, asset_path, filename, nb_streams, format_name, format_long_name, video_duration, bit_rate, encoding_media_id, sys_isrc)
        db_session.add(new_format_object)
        db_session.commit()
    except:
        print "ffprobe error"
        create_date = datetime.datetime.utcnow()
        asset_path = fpath
        fname = os.path.basename(fpath)
        filename = fname
        ffprobe_error = "ffprob error" 
        nb_streams = ffprobe_error
        format_name = ffprobe_error
        format_long_name = ffprobe_error 
        video_duration = ffprobe_error 
        bit_rate = ffprobe_error
        encoding_media_id = ffprobe_error 
        sys_isrc = ffprobe_error
        new_format_object = FormatMetadata(31, create_date, asset_path, filename, nb_streams, format_name, format_long_name, video_duration, bit_rate, encoding_media_id, sys_isrc)
        db_session.add(new_format_object)
        db_session.commit()

def parseJson(parsed_json):
    print parsed_json["format"]["filename"]
    filePathName = parsed_json["format"]["filename"]
    OriginPath = os.path.dirname(filePathName)
    fname = os.path.basename(filePathName)
    print fname
    baseFname = os.path.splitext(fname)[0]
    baseFnameEXT = os.path.splitext(fname)[1]
    asset_path = parsed_json["format"]["filename"]
    filename = fname
    print parsed_json["format"]["nb_streams"]
    nb_streams = parsed_json["format"]["nb_streams"]
    print parsed_json["format"]["format_name"]
    format_name = parsed_json["format"]["format_name"]
    print parsed_json["format"]["format_long_name"]
    format_long_name = parsed_json["format"]["format_long_name"]
    print parsed_json["format"]["duration"]
    video_duration = parsed_json["format"]["duration"]
    print parsed_json["format"]["bit_rate"]
    bit_rate = parsed_json["format"]["bit_rate"]
    encoding_media_id = "test"
    random_key = (my_random_string(10))
    sys_isrc = "VIACOM" + random_key
    create_date = datetime.datetime.utcnow()
    new_format_object = FormatMetadata(1, create_date, asset_path, filename, nb_streams, format_name, format_long_name, video_duration, bit_rate, encoding_media_id, sys_isrc)
    db_session.add(new_format_object)
    db_session.commit()
    format_object = db_session.query(func.max(FormatMetadata.id)).one()
    print "ID: %s" % format_object
    print type(format_object)
    format_id = format_object[0]
    for stream in parsed_json["streams"]:
        print stream["codec_type"], stream["index"]
        if stream["codec_type"] == "video":
            print "found video in index %s " % stream["index"]
            video_index_number = stream["index"]
            print stream["codec_name"]
            video_codec_name = stream["codec_name"]
            print stream["codec_long_name"]
            video_codec_long_name = stream["codec_long_name"]
            print stream["bit_rate"]
            video_bitrate = stream["bit_rate"]
            print stream["width"]
            video_width = stream["width"]
            print stream["height"]
            video_height = stream["height"]
            print stream["display_aspect_ratio"]
            video_aspect_ratio = stream["display_aspect_ratio"]
            print stream["r_frame_rate"]
            r_frame_rate = stream["r_frame_rate"]
            new_video_object = VideoMetadata(format_id, video_index_number, video_codec_name, video_codec_long_name, video_bitrate, video_height, video_width, video_aspect_ratio, r_frame_rate)
            db_session.add(new_video_object)
            db_session.commit()
        elif stream["codec_type"] == "audio":
            print "found audio in index %s " % stream["index"]
            print stream["index"]
            audio_index_no = stream["index"]
            print stream["codec_name"]
            audio_codec_name = stream["codec_name"]
            print stream["codec_long_name"]
            audio_codec_long_name = stream["codec_long_name"]
            print stream["sample_rate"]
            sample_rate = stream["sample_rate"]
            print stream["bits_per_sample"]
            bits_per_sample = stream["bits_per_sample"]
            audio_stream_language = "audio stream languge"
            audio_stream_type = "audio stream type"
            new_audio_object = AudioMetadata(format_id, audio_index_no, audio_codec_name, audio_codec_long_name, sample_rate, bits_per_sample, audio_stream_language, audio_stream_type)
            db_session.add(new_audio_object)
            db_session.commit()
        elif stream["codec_type"] == "data":
            print "found data in index %s " % stream["index"]
            data_index_no = stream["index"]
            data_codec_name = stream["codec_type"]
            new_data_object = DataMetadata(format_id, data_index_no, data_codec_name)
            print format_id, data_index_no, data_codec_name, "###"
            db_session.add(new_data_object)
            db_session.commit()
        elif stream["codec_type"] == "subtitle":
            print "found subtitle in index %s " % stream["index"]
            print stream["index"]
            subtitle_index_no = stream["index"]
            print stream["codec_type"]
            subtitle_codec_type = stream["codec_type"]
            print stream["codec_tag_string"]
            subtitle_codec_tag_string = stream["codec_tag_string"]
            print stream["tags"]["language"]
            subtitle_language_tag = stream["tags"]["language"]
            new_subtitle_object = SubtitleMetadata(format_id, subtitle_index_no, subtitle_codec_type, subtitle_codec_tag_string, subtitle_language_tag)
            db_session.add(new_subtitle_object)
            db_session.commit()
        else:
            print "noooooooo!"
            new_format_object.stateid=2

    filename = filename
    track_name = "track name"
    artist_name = "artist name"
    governing_agreement = "governing agreement"
    label_name = "label name"
    content_type = "content type"
    video_version = "video version"
    user_group = "user group"
    publisher = "publisher"
    composer = "composer"
    start_date = "start date"
    end_date = "end date"
    sys_isrc = sys_isrc
    label_isrc = "label isrc"
    music_video_keywords = "music video keywords"
    geo_codes = "geo codes"
    new_music_video_object = MusicVideo_Metadata(format_id, filename, track_name, artist_name, governing_agreement, label_name, content_type, video_version, user_group, publisher, composer, start_date, end_date, sys_isrc, label_isrc, music_video_keywords, geo_codes)      
    db_session.add(new_music_video_object)
    db_session.commit() 