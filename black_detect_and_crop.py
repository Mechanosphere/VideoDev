import os
import sys
import subprocess
import re
import pymysql
from collections import Counter
from Settings import *
from mviapp import app


def db_connect():
    try:
        conn = pymysql.connect(host=SQL_HOST, user=SQL_USER, passwd=SQL_PASS, db="mvi_live")
        conn.autocommit(1)
        cur = conn.cursor()
        return cur

    except Exception, e:
        raise


@app.task
def black_detect(video_id):
    try:
        cur = db_connect()
        cur.execute("SELECT localPath, width, height, stateId FROM videos WHERE id = %s", video_id)
        responses = cur.fetchall()
        if responses:
            for response in responses:
                local_file_path = response[0]
                width = response[1]
                height = response[2]
                stateid = response[3]
                if int(stateid) != 555:
                    print "video: ", video_id, " stateid not 555."
                    return
                # If this video < 10MB, set state id to 1 and redownload
                if os.path.getsize(local_file_path) >> 20 < 10:
                    print "video less than 10MB, need to be re-downloaded"
                    cur.execute("UPDATE videos SET stateId='1' WHERE id = %s", video_id)
                    return
                dummy_path = os.path.dirname(local_file_path)+'/dummy.mp4'
                # If dummy file already exists, delete it
                if os.path.exists(dummy_path):
                    os.remove(dummy_path)
                p = subprocess.Popen(["/usr/bin/ffmpeg", "-i", local_file_path, "-vf", "cropdetect=24:16:0",
                                      "-f", "rawvideo", "-y", dummy_path],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
                # Wait for p is finished. communicate() returns a tuple (stdoutdata, stderrdata)
                infos = p.communicate()[1]
                # Remove the dummy output file
                if os.path.exists(dummy_path):
                    os.remove(dummy_path)
                # infos = p.stderr.read()
                all_ratios = re.findall("crop=" + ".*", infos)
                most_common_ratio = Counter(all_ratios).most_common(1)
                print most_common_ratio
                # Example output of crop_ratio: crop=720:480:0:0
                crop_ratio = most_common_ratio[0][0]
                detected_width = crop_ratio.split('=')[1].split(':')[0]
                detected_height = crop_ratio.split('=')[1].split(':')[1]
                # if width != detected_width or height != detected_height:
                #     crop(video_id, local_file_path, crop_ratio)
                # Make 10 pixels of tolerance. If diff of width/height bigger than 10 pixel, we do the crop.
                if abs(int(width) - int(detected_width)) > 10 or abs(int(height) - int(detected_height)) > 10:
                    print "This video need to be cropped"
                    crop(video_id, local_file_path, crop_ratio, cur)
                else:
                    cur.execute("UPDATE videos SET stateId='6' WHERE id = %s", video_id)
        cur.close()
    except IOError:
        print "video file not found, need to be redownloaded"
        cur.execute("UPDATE videos SET stateId='1' WHERE id = %s", video_id)
        cur.close()
        return

    except Exception, e:
        print "video id: ", str(video_id)
        print str(e)
        cur.execute("UPDATE videos SET stateId='5' WHERE id = %s", video_id)
        cur.close()
        # raise


def crop(video_id, local_file_path, crop_ratio, cur):
    try:
        # Make the output name as the original one
        # For Labels other than WMG, change extension to mp4
        output_file_path = local_file_path.replace(".mpg", ".mp4")
        # For WMG, make sure the input and output filename are not same
        if output_file_path == local_file_path:
            os.rename(local_file_path, local_file_path+"_original")
            local_file_path = local_file_path + "_original"
            print "changed filename to ", local_file_path

        # If the output_path already exist (previously generated), we need to delete it
        if os.path.exists(output_file_path):
            os.remove(output_file_path)

        command = ["ffmpeg", "-i", local_file_path, "-vf", crop_ratio, "-codec:v", "libx264",
                   "-profile:v", "high", "-preset", "medium", "-b:v", "8000k", # -b:v make the bitrate to 8Mbps
                   "-codec:a", "libfaac", "-b:a", "256K", output_file_path]
        print command
        subprocess.check_call(command)


        detected_width = crop_ratio.split('=')[1].split(':')[0]
        detected_height = crop_ratio.split('=')[1].split(':')[1]
        # print "The video: "+video_id+" had been cropped to "+detected_width+"x"+detected_height
        # Use the cropped version if it bigger than 50MB
        if os.path.getsize(output_file_path) >> 20 > 50:
            try:
                # update_new_ratio(video_id, detected_width, detected_height)
                cur.execute("UPDATE videos SET stateId='6', width=%s, height=%s, localPath=%s WHERE id = %s",
                            (detected_width, detected_height, output_file_path, video_id))
                # Remove the original video file
                os.remove(local_file_path)
            except:
                cur.execute("UPDATE videos SET stateId='5' WHERE id = %s", video_id)
        # If not bigger than 20MB, this is not a real video but a audio track with static image, we use the original version
        # to avoid getting stuck in transcoding
        else:
            print "Output is too small, using original one"
            os.remove(output_file_path)
            os.rename(local_file_path, local_file_path[:-9])
            cur.execute("UPDATE videos SET stateId='6' WHERE id = %s", video_id)
    except subprocess.CalledProcessError:
        # change everything back so we could process it later
        print "crop video error"
        os.remove(output_file_path)
        if "_original" in local_file_path:
            os.rename(local_file_path, local_file_path[:-9])
            local_file_path = local_file_path[:-9]

        cur.execute("UPDATE videos SET stateId='5' WHERE id = %s", video_id)
    except Exception, e:
        print str(e)
        cur.execute("UPDATE videos SET stateId='5' WHERE id = %s", video_id)


def X(data):
    # Handle unicode issues
    try:
        return data.decode('utf8', 'strict').encode('utf8')
    except UnicodeDecodeError:
        return data.decode('unicode_escape')
    except ValueError:
        return data.encode('utf8')
    except:
        return data