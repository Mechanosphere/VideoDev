#!/usr/bin/python
import os
import fnmatch
from multiprocessing import Pool
from subprocess import Popen, PIPE, CalledProcessError

file_ext = ["*.mov", "*.mxf", "*.scc","*.mpg"]

path = "/Aspera/sony_dadc_nbcu_uds"
#path = "/Users/jonathanmathiesen/Desktop/origin"


def aspera_delivery(source_file):
    sony_aspera = "aspera-shares.dadcdigital.com"
    aspera_user_name = "dadc-nbcu-uds"
    aspera_pw = "iVDKQm2a"
    target_rate = "60000"
    print("File being send:", source_file)
    destination = "/SNEI-uds/nbcu/quickturn-tv/SNEI"
    with Popen("aspera", "shares", "upload", "-i", "-H", sony_aspera, "-u", aspera_user_name, "-p", aspera_pw,
         "--target-rate", target_rate, "-s", source_file, "-d", destination, "-v", stdout=PIPE, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            print(line, end='')  # process line here

    if p.returncode != 0:
        raise CalledProcessError(p.returncode, p.args)
    print("Deleting uploaded file: %s from source dir") % source_file
    os.remove(source_file)


if __name__ == "__main__":
    pool = Pool(1)
    tasks = []
    for root, dirs, filenames in os.walk(path):
        for extension in file_ext:
            for filename in fnmatch.filter(filenames, extension):
                source_file = os.path.join(root, filename)
                print("found file to upload:", source_file)
                tasks.append(pool.apply_async(aspera_delivery, args=(source_file,)))
    for task in tasks:
        task.get()
    pool.close()
    pool.join()
