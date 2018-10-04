import subprocess
from subprocess import CalledProcessError



command = ["ffmpeg",
           "-i", "/Users/jmathiesen/PycharmProjects/FFMPEG/wavecast_v1/9faf4ff8-88b2-4051-bb98-763864ed9206/final_video.mp4",
           "-i", "/Users/jmathiesen/PycharmProjects/FFMPEG/wavecast_v1/9faf4ff8-88b2-4051-bb98-763864ed9206/Wavecastlogo.png",
           "-filter_complex", 'overlay=main_w-overlay_w-5:5',
           "/Users/jmathiesen/PycharmProjects/FFMPEG/wavecast_v1/9faf4ff8-88b2-4051-bb98-763864ed9206/wtrmark_final.mp4"]

def encode_wtrmark(command):
    try:
        ffmpeg_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        for line in ffmpeg_process.stdout:
            print(line)
        return ffmpeg_process
    except Exception as Error:
        print(Error)



encode_wtrmark(command)