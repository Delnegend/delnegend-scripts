from asyncio import subprocess
from os import chdir, listdir
from os.path import isfile, join
from shutil import move
from sys import argv
import subprocess

def main():
    folders = getFolders(".")
    userArg = "zip" if len(argv) == 1 or argv[1] != "7z" else "7z"
    try:
        for folder in folders:
            # if the folder is not empty
            if len(listdir(folder)) > 0:
                chdir(folder)
                if userArg == "7z":
                    compress_7z(folder)
                else:
                    compress_zip(folder)
                move(f'{folder}.{userArg}', "..")
                chdir("..")
    except Exception as e:
        print(e)
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