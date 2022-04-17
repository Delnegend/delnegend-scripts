import subprocess, os, argparse
import concurrent.futures

def print_sign(text):
    top_bottom_bar = '=' * (len(text) + 8)
    space = '=' + ' ' * (len(text) + 6) + '='
    message = '=' + ' ' * 3 + text + ' ' * 3 + '='
    print(top_bottom_bar)
    print(space)
    print(message)
    print(space)
    print(top_bottom_bar)

def convert(file):
    filename = file.replace("."+file.split('.')[-1], "")
    subprocess.run(f'cjxl "{file}" "{filename}.jxl" -q 100 -e 8', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

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

    args = getArgs()
    convert_failed = []

    if args.i:
        convert(args.i)
    if not args.i:
        files = getFiles(os.getcwd())
        with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
            for item in files:
                curr_thread = executor.submit(convert, item)
                if not curr_thread.result():
                    print(f'{item} converted to .jxl')
                else:
                    convert_failed.append(item)
        if len(convert_failed) > 0:
            print_sign(f'{len(convert_failed)} files failed to convert to jxl')
            for item in convert_failed:
                print(item)
        print_sign("Press Enter to exit...")
        input()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
    exit()