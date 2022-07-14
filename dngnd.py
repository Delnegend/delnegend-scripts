import os
import subprocess
import cv2
from os import path
from cv2 import resize

THREADS = 4


def hsize(size):
    # human readable size
    size = float(size)
    for x in ['bytes', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return "%3.2f %s" % (size, x)
        size /= 1024.0
    return size


def htime(seconds):
    if seconds >= 60*60:
        return f"{int(seconds/3600)}h{int(seconds%3600/60)}m{int(seconds%60)}s"
    elif seconds >= 60:
        return f"{int(seconds/60)}m{int(seconds%60)}s"
    else:
        return f"{seconds:.2f}s"


def list_files(path: str, ext: list, recursive=True, get_full_path=False):
    full_path = os.path.abspath(path) if not os.path.isabs(path) else path
    rel_path = os.path.relpath(path, os.getcwd())
    files = []
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            if len(ext) > 0 and os.path.splitext(file)[1].lower() in ext:
                files.append(os.path.join(full_path, file) if get_full_path else os.path.join(rel_path, file))
            elif len(ext) == 0:
                files.append(os.path.join(full_path, file) if get_full_path else os.path.join(rel_path, file))
        else:
            if recursive:
                files += list_files(os.path.join(path, file), ext, recursive, get_full_path)
    return files


def list_folders(path: str, recursive = True):
    # list folders recursively in path
    folders = []
    for folder in os.listdir(path):
        if os.path.isdir(os.path.join(path, folder)):
            folders.append(os.path.join(path, folder))
            if recursive:
                folders += list_folders(os.path.join(path, folder), recursive)
    return folders


def dm_ffprobe(path: str):
    try:
        result = subprocess.run(
            f'ffprobe -v error -select_streams v -show_entries stream=width,height -of csv=p=0:s=x "{path}"',
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        w, h = result.stdout.decode('utf-8').split('x')
        return (int(w), int(h))
    except:
        return (0, 0)


def dimension(path: str):
    if os.path.splitext(path)[1] in [".bmp", ".dib", ".jpeg", ".jpg", ".jpe", ".jp2", ".png", ".webp", ".pbm", ".pgm", ".ppm", ".pxm", ".pnm", ".pfm", ".sr", ".ras", ".tiff", ".tif", ".exr", ".hdr", ".pic"]:
        try:
            h, w, _ = cv2.imread(path).shape
            return (w, h)
        except:
            return dm_ffprobe(path)
    else:
        return dm_ffprobe(path)


def print_sign(sign: str, size: str):
    slen = len(sign.encode('utf-8'))
    if size == "main":
        # print("\n")
        print("="*(slen+6))
        print("=" + " "*(slen+4) + "=")
        print(f'=  {sign}  =')
        print("=" + " "*(slen+4) + "=")
        print("="*(slen+6))
        # print("\n")
    elif size == "small":
        # print("\n")
        print("-"*slen + "\n" + sign + "\n" + "-"*slen)
        # print("\n")


def report_results(files_len: str, orig_size: str, new_size: str, start_timer: str, end_timer: str):
    h_size_orig, h_size_new = hsize(orig_size), hsize(new_size)
    ratio = f'{round((new_size/orig_size)*100, 2)}%'
    time_taken = htime(end_timer - start_timer)
    return f'{files_len} file(s): {h_size_orig} -> {h_size_new} ~ {ratio} | {time_taken}'