import os
import datetime


test_path_list = ['/Users/jrm/Documents/paths/path1', '/Users/jrm/Documents/paths/path2'] # use this list to test the paths

delete_7_day_list = ['QC_BEFORE_DELIVERY/',
                     'RESTORE_MEDIA',
                     'TRANSCODE/VANTAGE/X and Y/',
                     'MEDIA/SPECIAL_PROJECTS/TEXTLESS_QC/FAIL',
                     'MEDIA/SPECIAL_PROJECTS/TEXTED_OFR_QC/FAIL',
                     'MEDIA/INCOMING/STUDIOPOST_RESTORES',
                     'DELIVERY/',
                     'MEDIA/CONVERSIONS']

delete_3_day_list = ['DMO/USAC3VOD/USAC3_VOD_WATCH/',
                     'DMO/XCODE_WATCH/TO_INCOMING/STEREO']

delete_14_day_list = ['DMO/NEW_MEDIA_INCOMING/MACCAPTION_CCVC_ENCODE',
                      'MEDIA/INCOMING/EC_POST/INGEST_PREP/CC_PROXY_TRANSCODE',
                      'MEDIA/INCOMING/EC_POST/INGEST_PREP/TO_RAF_INBOUND_SHORTFORM_AND_ARCHIVE',
                      'MEDIA/INCOMING/EC_POST/INGEST_PREP/NEW_CC_POST_MASTER',
                      'DMO/XCODE_WATCH/TO_INCOMING/5.1',
                      'MEDIA/INCOMING/LATE_NIGHT_MEYERS/RECEIVE_AUTO_DOWNMIX',
                      'MEDIA/INCOMING/TNT_FALLON/RECEIVE_AUTO_DOWNMIX',
                      'MEDIA/INCOMING/EC_POST/NEW_CC_SOURCE_MASTER']

exclude_path_list = ['path/1', 'path/2']

def delete_7_days(test_path_list):
    for paths in test_path_list:
        print('checking path:{}'.format(paths))
        for dirpath, dirnames, filenames in os.walk(paths):
            for file in filenames:
                if file.startswith('C_') or not file.startswith('+T'):
                    print('found file: {}'.format(file))
                    curpath = os.path.join(dirpath, file)
                    file_modified = datetime.datetime.fromtimestamp(os.path.getmtime(curpath))
                    if datetime.datetime.now() - file_modified > datetime.timedelta(days=7):
                        print('found file to delete: {}'.format(file))
                        os.remove(curpath)
                elif file.startswith('+T'):
                    print('archive file: {}'.format(file))


def delete_3_days(test_path_list):
    for paths in test_path_list:
        print(paths)
        for dirpath, dirnames, filenames in os.walk(paths):
            for file in filenames:
                if file.startswith('C_') or not file.startswith('+T'):
                    print('found file:{}'.format(file))
                    curpath = os.path.join(dirpath, file)
                    file_modified = datetime.datetime.fromtimestamp(os.path.getmtime(curpath))
                    if datetime.datetime.now() - file_modified > datetime.timedelta(days=3):
                        os.remove(curpath)
                elif file.startswith('+T'):
                    print('archive file: {}'.format(file))


def delete_14_days(delete_14_day_list):
    for paths in delete_14_day_list:
        for dirpath, dirnames, filenames in os.walk(paths):
            for file in filenames:
                if file.startswith('C_') or not file.startswith('+T'):
                    curpath = os.path.join(dirpath, file)
                    file_modified = datetime.datetime.fromtimestamp(os.path.getmtime(curpath))
                    if datetime.datetime.now() - file_modified > datetime.timedelta(days=14):
                        os.remove(curpath)
                elif file.startswith('+T'):
                    print('archive file: {}'.format(file))


delete_7_days(test_path_list)