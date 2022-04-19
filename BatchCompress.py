from asyncio import subprocess
from os import chdir, listdir
from os.path import isfile, join
from shutil import move
from sys import argv
import subprocess

def main():
    folders = getFolders(".")
    type = str(argv[1]).lower()
    try:
        for folder in folders:
            chdir(folder)
            if not is_empty(folder):
                if type == "7z":
                    compress_7z(folder)
                else:
                    compress_zip(folder)
                move(f'{folder}.{type}', "..")
            chdir("..")
    except:
        print("You must specify a type of compression as a first argument: 7z or zip")
def getFolders(path):
    return [f for f in listdir(path) if not isfile(join(path, f))]

# check if the directory is empty
def is_empty(dir):
    return len(listdir(dir)) == 0

def compress_zip(item):
    subprocess.run(f'7z.exe a -bt -tzip -x"!*.ini" -r "{item}.zip" *.*', shell=True, check=True)

def compress_7z(item):
    subprocess.run(f'7z.exe a -bt -t7z -x"!*.ini" -m0=lzma2:d1024m -mx=9 -mfb=64 -md=32m -ms=on -r "{item}.7z" *.*', shell=True, check=True)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
    exit()