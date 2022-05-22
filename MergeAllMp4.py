import os
from glob import glob
from shutil import move
from re import search
import subprocess as sp
from concurrent.futures import ProcessPoolExecutor, as_completed


def list_folders(dir):
    folders = []
    for name in os.listdir(dir):
        path = os.path.join(dir, name)
        if os.path.isdir(path):
            folders.append(path)
    return folders


def list_files(dir, recurse=True):
    files = []
    for name in os.listdir(dir):
        path = os.path.join(dir, name)
        if os.path.isfile(path):
            files.append(path)
        elif recurse:
            files.extend(list_files(path, recurse))
    return files


def is_corrupt(file):
    ffmpeg_check = f'ffmpeg -y -i "{file}" -t 2 -r 0.5 "{file}.png"'
    sp.call(ffmpeg_check, shell=True, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    if os.path.exists(f"{file}.png"):
        os.remove(f"{file}.png")
        return False
    else:
        return True


def main():
    all_parts = list_folders(".")
    for item in all_parts:
        # if item doesn't contain underscore and regex match \d{10}
        if not search("_", item) and search("\d{10}", item):
            day_folder = item[slice(6)] + "_" + \
                item[slice(6, 8)] + "_" + item[slice(8, 10)]
            if not os.path.exists(day_folder):
                os.mkdir(day_folder)
            move(item, day_folder)
    day_vids = list_folders(".")

    # for each folder in YYYY_MM_DDs, merge every mp4 file into YYYY_MM_DD.mkv
    for day_vid in day_vids:
        if not search("\d{4}_\d{2}_\d{2}", day_vid):
            continue
        os.chdir(day_vid)
        all_parts_in_day = list_files(".")

        # check for corrupt files and remove them
        print(f"Checking for corrupt files of {day_vid}...")
        corrupted_files = []
        with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
            tasks = {executor.submit(is_corrupt, file): file for file in all_parts_in_day}
            for task in as_completed(tasks):
                file = tasks[task]
                try:
                    if not task.result():
                        continue
                except:
                    print(f"- {file} is corrupted")

        for file in corrupted_files:
            print(f"- {file} is corrupted")
        if corrupted_files:
            for file in corrupted_files:
                os.remove(file)

        # create merge.txt, contains path of every MP4 in YYYY_MM_DD and use ffmpeg to merge them
        if not os.path.exists("merge.txt"):
            with open("merge.txt", "w") as f:
                f.write("")
        for file in all_parts_in_day:
            if not file.endswith(".mp4"):
                continue
            with open("merge.txt", "a") as f:
                file = file.replace("\\", "/")
                f.write(f"file {file}\n")
        print("Merging files...")
        ffmpeg_merge_all = f'ffmpeg -f concat -safe 0 -i merge.txt -c copy "..\{day_vid}.mkv"'

        if not os.path.exists("merge.log"):
            with open("merge.log", "w") as f:
                f.write("")
        with open("merge.log", "a") as f:
            sp.call(ffmpeg_merge_all, shell=True, stdout=f, stderr=f)
        os.remove("merge.txt")

        os.chdir("..")
    print("Press any key to exit...")
    input()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
