import os
import subprocess
import shutil
import pkg.list

def main():
    files = pkg.list.file(".", [".mkv"], recursive=True)
    for file in files:
        folder_name = os.path.splitext(file)[0]
        convert_to_mp4 = f'ffmpeg -i {file} -codec copy "output.mp4"'
        split_to_hls = f'ffmpeg -i output.mp4 -codec copy -start_number 0 -hls_time 15 -hls_list_size 0 -f hls index.m3u8'
        os.mkdir(folder_name)
        shutil.move(file, folder_name)
        os.chdir(folder_name)
        subprocess.run(convert_to_mp4, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(split_to_hls, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.remove('output.mp4')
        shutil.move(file, '..')
        os.chdir('..')

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
    input("\nPress enter to exit...")
