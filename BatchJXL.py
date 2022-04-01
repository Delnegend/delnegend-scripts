import subprocess, os
from multiprocessing import Process
import time

def main():
    files = getFiles(".\\")
    procs = []

    while True:

        for proc in procs:
            if not proc.is_alive():
                procs.remove(proc)

        if (len(procs) < 4 and len(files) > 0):
            proc = Process(target=convert, args=(files[0],))
            procs.append(proc)
            proc.start()
            files.pop(0)
            sign(f'Queue: {str(len(procs))}, files remaining: {str(len(files))}')
        elif (len(procs) == 0 and len(files) == 0):
            print("the work is done")
            break
        time.sleep(1)

def convert(file):
    filename = file.replace("."+file.split('.')[-1], "")
    subprocess.run(f'cjxl "{file}" "{filename}.jxl" -q 100 -e 8', shell=True, check=True)

# get files in folder
def getFiles(path):
    files = []
    for file in os.listdir(path):
        supported_format = ["exr", "gif", "jpeg", "jpg", "pfm", "pgm", "ppm", "pgx", "png"]
        if file.split('.')[-1] in supported_format:
            files.append(file)
    return files

def sign(text:str):
    print("="*40)
    print("=\n"*2+"=")
    print("="+"      "+text)
    print("=\n"*2+"=")
    print("="*40)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
    exit()
