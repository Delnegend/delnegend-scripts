import os
import subprocess
import glob
import shutil

def main():
    files = getFiles(os.getcwd())
    for file in files:
        extension = file.split('.')[-1]
        folder_name = file.replace('.' + extension, '')
        convert_to_mp4 = f'ffmpeg -i {file} -codec copy "output.mp4"'
        split_to_hls = f'ffmpeg -i output.mp4 -codec copy -start_number 0 -hls_time 15 -hls_list_size 0 -f hls index.m3u8'
        os.mkdir(folder_name)
        shutil.move(file, folder_name)
        os.chdir(folder_name)
        subprocess.call(convert_to_mp4, shell=True)
        subprocess.call(split_to_hls, shell=True)
        os.remove('output.mp4')
        shutil.move(file, '..')
        os.chdir('..')

def getFiles(path):
    files = []
    for file in os.listdir(path):
        supported_format = ["mkv"]
        if file.split('.')[-1].lower() in supported_format:
            files.append(file)
    return files


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
    exit()
