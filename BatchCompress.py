from ast import arg
from asyncio import subprocess
from os import chdir, listdir
from os.path import isfile, join
from shutil import move
from sys import argv
import subprocess

def main():
    folders = getFolders(".")
    type = argv[1]
    try:
        if type == "7z":
            for folder in folders:
                chdir(folder)
                compress_7z(folder)
        elif type == "zip":
            for folder in folders:
                chdir(folder)
                compress_zip(folder)
        else:
            print("Type must be 7z or zip")
        move(f'{folder}.{type}', "..")
        chdir("..")
    except Exception as e:
        print("You must specify a type of compression as a first argument: 7z or zip")
def getFolders(path):
    return [f for f in listdir(path) if not isfile(join(path, f))]

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