import subprocess, os, argparse
import concurrent.futures
from dngnd import print_sign

def convert(file):
    filename = file.replace("."+file.split('.')[-1], "")
    if (subprocess.run(f'cjxl "{file}" "{filename}.jxl" -q 100 -e 8', shell=True, check=True) == 0):
        print_sign(f'{file} converted to {filename}.jxl')
        return True;
    else:
        print_sign(f'{file} failed to convert to {filename}.jxl')
        return False;

def getFiles(path):
    files = []
    for file in os.listdir(path):
        supported_format = ["exr", "gif", "jpeg", "jpg", "pfm", "pgm", "ppm", "pgx", "png"]
        if file.split('.')[-1].lower() in supported_format:
            files.append(file)
    return files

def getArgs():
    parser = argparse.ArgumentParser(description="Convert image files to jxl. If none argument is given, all files in current directory will be converted.")
    parser.add_argument("-i", help="Input supported file (jpg, png, gif, exr, jpeg, pfm, pgm, ppm, pgx)", type=str, required=False)
    return parser.parse_args()

def main():
    args = getArgs();
    if args.i:
        convert(args.i)
    if not args.i:
        files = getFiles(os.getcwd())
        with concurrent.futures.ProcessPoolExecutor() as executor:
            executor.map(convert, files)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
    exit()