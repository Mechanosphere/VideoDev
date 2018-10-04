from pymongo import MongoClient
import json
client = MongoClient('localhost:27017')
db = client.MediaProcessing

def contruct_concat_cmd(video_local_url_list, job_id, db_id):
    concat_video = 'concat_video.mp4'
    video_out = '/Users/jmathiesen/PycharmProjects/FFMPEG/wavecast_v1/' + job_id + '/' + concat_video
    cmd = []
    video_map_list = []
    counter = 0
    for item in video_local_url_list:
        cmd.append("-i")
        cmd.append(item)
        video_map = '[' + str(counter) + ':v:0]'
        video_map_list.append(video_map)
        counter = counter + 1
    concat_str = "concat=n=" + str(counter) + ":v=1 [v]"
    str_video_map = " ".join(video_map_list)
    cmd.append("-filter_complex")
    filter_complex = str_video_map + ' ' + concat_str
    filter_complex = str(filter_complex)
    cmd.append(filter_complex)
    cmd.append("-map")
    cmd.append("[v]")
    cmd.append(video_out)
    cmd.insert(0, 'ffmpeg')
    print('{}'.format(cmd))
    json_cmd = json.dumps(cmd)
    db.JobProcess.update({'_id': db_id},
                              {'$push': {
                                  'ffmpeg_cmds': {
                                      'ffmpeg_concat_cmd': json_cmd,
                                                                                  }
                                         }})
    return cmd

def contruct_merge_audio_cmd(concat_video_url, audio_url, job_id, db_id):
    final_video = 'final_video.mp4'
    video_out = '/Users/jmathiesen/PycharmProjects/FFMPEG/wavecast_v1/' + job_id + '/' + final_video
    video_item = concat_video_url
    audio_item = audio_url
    map_cmd = '-map'
    video_map_cmd = '0:v:0'
    audio_map_cmd = '1:a:0'
    cmd = []
    cmd.append('ffmpeg')
    cmd.append("-i")
    cmd.append(video_item)
    cmd.append("-i")
    cmd.append(audio_item)
    cmd.append("-c")
    cmd.append("copy")
    cmd.append(map_cmd)
    cmd.append(video_map_cmd)
    cmd.append(map_cmd)
    cmd.append(audio_map_cmd)
    cmd.append(video_out)
    json_cmd = json.dumps(cmd)
    db.JobProcess.update({'_id': db_id},
                              {'$push': {
                                  'ffmpeg_cmds': {
                                      'ffmpeg_add_audio_cmd': json_cmd,
                                                                                  }
                                         }})
    return cmd


def add_watermarking(src_video_path, src_watermark_path, job_id, db_id):
    wtr_video = 'wtrmark_final.mp4'
    video_out = '/Users/jmathiesen/PycharmProjects/FFMPEG/wavecast_v1/' + job_id + '/' + wtr_video
    overlay_x = str(35)
    overlay_y = str(35)
    over_lay_filter = 'overlay=' + overlay_x + ':' + overlay_y
    cmd = []
    cmd.append('ffmpeg')
    cmd.append('-i')
    cmd.append(src_video_path)
    cmd.append('-i')
    cmd.append(src_watermark_path)
    cmd.append('-filter_complex')
    cmd.append(over_lay_filter)
    cmd.append(video_out)
    json_cmd = json.dumps(cmd)
    db.JobProcess.update({'_id': db_id},
                         {'$push': {
                             'ffmpeg_cmds': {
                                 'ffmpeg_add_watermark_cmd': json_cmd,
                             }
                         }})
    return cmd