from os import remove, mkdir, chdir
from os.path import exists
from shutil import move
from re import search
from subprocess import Popen, call, DEVNULL
from dngnd import *
from concurrent.futures import ProcessPoolExecutor, as_completed


def is_corrupt(file):
    ffmpeg_check = f'ffmpeg -y -i "{file}" -t 2 -r 0.5 "{file}.png"'
    call(ffmpeg_check, shell=True, stdout=DEVNULL, stderr=DEVNULL)
    if exists(f"{file}.png"):
        remove(f"{file}.png")
        return False
    else:
        return True


def main():
    all_parts = list_folders(".", False)
    for item in all_parts:
        # if item doesn't contain underscore and regex match \d{10}
        if not search("_", item) and search("\d{10}", item):
            day_folder = item[slice(6)] + "_" + \
                item[slice(6, 8)] + "_" + item[slice(8, 10)]
            if not exists(day_folder):
                mkdir(day_folder)
            move(item, day_folder)
    day_vids = list_folders(".", False)

    # for each folder in YYYY_MM_DDs, merge every mp4 file into YYYY_MM_DD.mkv
    for day_vid in day_vids:
        if not search("\d{4}_\d{2}_\d{2}", day_vid):
            continue
        chdir(day_vid)
        all_parts_in_day = list_files(".", [], True)

        # check for corrupt files and remove them
        print(f"Checking for corrupt files of {day_vid}...")
        corrupted_files = []
        with ProcessPoolExecutor(max_workers=THREADS) as executor:
            tasks = {executor.submit(is_corrupt, file): file for file in all_parts_in_day}
            for task in as_completed(tasks):
                try:
                    if not task.result():
                        continue
                except:
                    print(f"- {tasks[task]} is corrupted")

        for file in corrupted_files:
            print(f"- {file} is corrupted")
        if corrupted_files:
            for file in corrupted_files:
                remove(file)

        # create merge.txt, contains path of every MP4 in YYYY_MM_DD and use ffmpeg to merge them
        if not exists("merge.txt"):
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

        if not exists("merge.log"):
            with open("merge.log", "w") as f:
                f.write("")
        with open("merge.log", "a") as f:
            call(ffmpeg_merge_all, shell=True, stdout=f, stderr=f)
        remove("merge.txt")

        chdir("..")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
    input("\nPress enter to exit...")
