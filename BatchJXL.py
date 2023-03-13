import os
import pkg
from time import time
from subprocess import run, DEVNULL
from argparse import ArgumentParser
from concurrent.futures import ProcessPoolExecutor, as_completed

THREADS = 4

def get_args():
    parser = ArgumentParser(description="JPEG XL Batch en/decoder. Supported formats: exr, gif, jpeg, jpg, pfm, pgm, ppm, pgx, png")
    parser.add_argument("-d", help="Decode jxl file to png", action="store_true", required=False)
    parser.add_argument("-exit", help="Exit after conversion", action="store_true", required=False)
    parser.add_argument("-f", "--formats", help="File format will be converted, seperated by a space", type=str, required=False)
    return parser.parse_args()


def report_size(old_file, new_file):
    old_size = os.path.getsize(old_file)
    new_size = os.path.getsize(new_file)
    old_size_to_print = pkg.human_readable.size(old_size)
    new_size_to_print = pkg.human_readable.size(new_size)
    return f"{old_size_to_print} -> {new_size_to_print} ~ {round((new_size/old_size)*100, 2)}%"


def encode(file):
    filename = file.replace("."+file.split('.')[-1], "")
    try:
        run(f'cjxl "{file}" "{filename}.jxl" -q 100 -e 8', stdout=DEVNULL, stderr=DEVNULL)
        return True
    except:
        return False


def decode(file):
    filename = file.replace("."+file.split('.')[-1], "")
    try:
        run(f'djxl "{file}" "{filename}.png" -q 100', stdout=DEVNULL, stderr=DEVNULL)
        return True
    except:
        return False


convert_failed = []

def main(args):

    # Encode to jxl
    if not args.d:
        before_size, after_size = 0, 0
        timer = time()
        formats = args.formats.split(' ') if args.formats else [".exr", ".gif", ".jpeg", ".jpg", ".pfm", ".pgm", ".ppm", ".pgx", ".png"]
        files = pkg.list.list_files(".", formats, True)
        with ProcessPoolExecutor(max_workers=THREADS) as executor:
            tasks = {executor.submit(encode, file): file for file in files}
            for task in as_completed(tasks):
                res = tasks[task]
                if task.result():
                    before_size += os.path.getsize(res)
                    after_size += os.path.getsize(res.replace("."+res.split('.')[-1], ".jxl"))
                    print(f"==> SUCCESS: {os.path.basename(res)} | {report_size(res, res.replace('.'+res.split('.')[-1], '.jxl'))}")
                else:
                    convert_failed.append(res)

    # Decode jxl to png
    if args.d:
        files = pkg.list.file(os.getcwd(), [".jxl"], True)
        timer = time()
        with ProcessPoolExecutor(max_workers=THREADS) as executor:
            tasks = {executor.submit(decode, file): file for file in files}
            for task in as_completed(tasks):
                res = tasks[task]
                if task.result():
                    print(f"==> SUCCESS: {os.path.basename(res)}")
                else:
                    convert_failed.append(res)

    converted_count = len(files) - len(convert_failed)
    time_taken_readable = pkg.human_readable.time(time() - timer)
    print(f"\n==> {converted_count} file(s) converted in {time_taken_readable}")
    if not args.d:
        before_size_readable = pkg.human_readable.size(before_size)
        after_size_readable = pkg.human_readable.size(after_size)
        ratio = round((after_size/before_size)*100, 2)
        time_taken_readable = pkg.human_readable.time(time() - timer)
        print(f'{before_size_readable} -> {after_size_readable} ~ {ratio}% | {time_taken_readable}')
    if len(convert_failed) > 0:
        print(f'\n==> {len(convert_failed)} file(s) failed to convert')
        for item in convert_failed:
            print(os.path.basename(item))


if __name__ == '__main__':
    try:
        args = get_args()
        main(args)
    except Exception as e:
        print(e)
    if args.exit:
        if len(convert_failed) > 0:
            exit(1)
        exit(0)
    input("\nPress Enter to exit...\n")
