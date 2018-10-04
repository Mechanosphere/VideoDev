import urllib.request
import os
from pymongo import MongoClient

client = MongoClient('localhost:27017')
db = client.MediaProcessing

def download_audio(audio_src_url, media_local_dir):
    audio_src_url = audio_src_url
    audio_path = media_local_dir
    audio_filename = os.path.basename(audio_src_url)
    audio_local_dir = os.path.join(audio_path, audio_filename)
    urllib.request.urlretrieve(audio_src_url, audio_local_dir)
    print('downloaded Audio: {}, to: {}'.format(audio_src_url, audio_path))
    return audio_local_dir


def download_watermark(watermark_src_url, media_local_dir):
    watermark_src_url = watermark_src_url
    watermark_path = media_local_dir
    watermark_filename = os.path.basename(watermark_src_url)
    watermark_local_dir = os.path.join(watermark_path, watermark_filename)
    urllib.request.urlretrieve(watermark_src_url, watermark_local_dir)
    print('downloaded watermark: {}, to: {}'.format(watermark_src_url, watermark_path))
    return watermark_local_dir

def download_images(img_src_path, media_local_dir):
    img_src_path = img_src_path
    local_path = media_local_dir
    image_filename = os.path.basename(img_src_path)
    img_local_dir = os.path.join(local_path, image_filename)
    urllib.request.urlretrieve(img_src_path, img_local_dir)
    print('dloaded: {}, to: {}'.format(img_src_path, img_local_dir))
    return img_local_dir
