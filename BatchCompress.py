from asyncio import subprocess
from os import chdir, listdir
from os.path import isfile, join
from shutil import move
from argparse import ArgumentParser
from cv2 import repeat
import concurrent.futures
import subprocess

def main():
    params = params()
    for item in [f for f in listdir(".") if not isfile(join(".", f))]:
        chdir(item)
        with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
            executor.map(compress, item, repeat(params.type))
        move(f'{item}.{type}', "..")
        chdir("..")

def compress(item, type):
    zip = f'7z.exe a -bt -x"!*.ini" -r "{item}.zip" *.*'
    seven_z = f'7z a -t7z -x"!*.ini" -m0=lzma2:d1024m -mx=9 -mfb=64 -md=32m -ms=on -r "{item}.7z" *.*'
    subprocess.run(zip if type == "zip" else seven_z, shell=True, check=True)

def params():
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