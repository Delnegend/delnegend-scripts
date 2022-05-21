import subprocess, os, argparse
from concurrent.futures import ProcessPoolExecutor, as_completed

# list files recursively
def getFiles(path, ext):
    files = []
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            if file.split('.')[-1] in ext:
                files.append(os.path.join(path, file))
        else:
            files += getFiles(os.path.join(path, file), ext)
    return files

def encode(file):
    filename = file.replace("."+file.split('.')[-1], "")
    subprocess.run(f'cjxl "{file}" "{filename}.jxl" -q 100 -e 8', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def decode(file):
    filename = file.replace("."+file.split('.')[-1], "")
    subprocess.run(f'djxl "{file}" "{filename}.png" -q 100', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def getArgs():
    parser = argparse.ArgumentParser(description="JPEG XL Batch Encoder/Decoder. Supported formats: exr, gif, jpeg, jpg, pfm, pgm, ppm, pgx, png")
    parser.add_argument("-d", help="Decode jxl file to png", action="store_true", required=False)
    return parser.parse_args()

def main():
    args = getArgs()
    convert_failed = []

    # Encode to jxl
    if not args.d:
        files = getFiles(os.getcwd(), ["exr", "gif", "jpeg", "jpg", "pfm", "pgm", "ppm", "pgx", "png"])
        with ProcessPoolExecutor(max_workers=4) as executor:
            tasks = {executor.submit(encode, file): file for file in files}
            for task in as_completed(tasks):
                file = tasks[task]
                try:
                    if not task.result():
                        print(f"{file} converted successfully to jxl")
                except:
                    convert_failed.append(file)

    # Decode jxl to png
    if args.d:
        files = getFiles(os.getcwd(), ["jxl"])
        with ProcessPoolExecutor(max_workers=4) as executor:
            tasks = {executor.submit(decode, file): file for file in files}
            for task in as_completed(tasks):
                file = tasks[task]
                try:
                    if not task.result():
                        print(f"{file} converted successfully to png")
                except:
                    convert_failed.append(file)

    if len(convert_failed) > 0:
        print(f'{len(convert_failed)} files failed to convert')
        for item in convert_failed:
            print(item)

    print("\nPress Enter to exit...\n")
    input()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
    exit()
