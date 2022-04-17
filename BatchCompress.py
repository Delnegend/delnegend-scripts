from asyncio import subprocess
from os import chdir, listdir
from os.path import isfile, join
from shutil import move
from argparse import ArgumentParser
from cv2 import repeat
import concurrent.futures
import subprocess

def main():
    params = getParams()
    folders = getFiles(".")
    for folder in folders:
        chdir(folder)
        if params.type == "zip":
            compress_zip(folder)
        else if params.type == "7z":
            compress_7z(folder)
        move(f'{folder}.{type}', "..")
        chdir("..")

def getFiles(path):
    return [f for f in listdir(path) if not isfile(join(path, f))]

def compress_zip(item):
    subprocess.run(zip = f'7z.exe a -bt -x"!*.ini" -r "{item}.zip" *.*', shell=True, check=True)

def compress_7z(item):
    subprocess.run(f'7z a -t7z -x"!*.ini" -m0=lzma2:d1024m -mx=9 -mfb=64 -md=32m -ms=on -r "{item}.7z" *.*', shell=True, check=True)

def getParams():
    parser = ArgumentParser("BatchCompress.py")
    parser.add_argument("-type", help="zip or 7z", type=str)
    params = parser.parse_args()
    if params.type not in ["zip", "7z"]:
        raise Exception("-type must be zip or 7z")
    return params

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
    exit()