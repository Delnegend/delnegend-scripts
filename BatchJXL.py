import subprocess, os
import concurrent.futures

def main():
    files = getFiles(".\\")
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(convert, files)

def convert(file):
    filename = file.replace("."+file.split('.')[-1], "")
    subprocess.run(f'cjxl "{file}" "{filename}.jxl" -q 100 -e 8', shell=True, check=True)

def getFiles(path):
    files = []
    for file in os.listdir(path):
        supported_format = ["exr", "gif", "jpeg", "jpg", "pfm", "pgm", "ppm", "pgx", "png"]
        if file.split('.')[-1] in supported_format:
            files.append(file)
    return files

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
    exit()
