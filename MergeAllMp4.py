import re
import os
import shutil
import subprocess as sp
from concurrent.futures import ProcessPoolExecutor, as_completed


def norm(path: str) -> str:
    return os.path.normpath(path).replace("\\", "/")

def list(type: str, path: str, ext: list, recursive: bool):
    result = []
    for root, dirs, files in os.walk(path):
        if type == "file":
            for file in files:
                if not ext or file.split(".")[-1] in ext:
                    result.append(norm(os.path.join(root, file)))
        elif type == "folder":
            for folder in dirs:
                result.append(norm(os.path.join(root, folder)))
        if not recursive:
            break
    return result

class BCOLOR:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Footage(object):

    def __init__(self, host_folder: str):
        self.host_folder = ""
        self.parts = []
        self.host_folder = host_folder
        for item in list("file", self.host_folder, ["mp4"], True):
            self.parts.append(item)

    def isCorrupt(self, file: str) -> bool:
        sp.run(f'ffmpeg -y -i "{file}" -t 2 -r 0.5 "{file}.jpg"', shell=True, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        if os.path.exists(f"{file}.jpg"):
            os.remove(f"{file}.jpg")
            return False
        return True

    def checkCorrupt(self) -> None:
        with ProcessPoolExecutor(max_workers=8) as executor:
            tasks = {executor.submit(self.isCorrupt, file): file for file in self.parts}
            for task in as_completed(tasks):
                try:
                    result = task.result()
                except Exception as e:
                    print(e)
                else:
                    print(BCOLOR.FAIL + tasks[task] + BCOLOR.ENDC) if result else None

    def printList(self):
        for line in self.parts:
            print(line)

    def writeList(self):
        with open(f"{self.host_folder}/list.txt", "w") as file:
            file.write("")
        for line in self.parts:
            line = line.replace(f"{self.host_folder}/", "")
            with open(f"{self.host_folder}/list.txt", "a") as file:
                file.write(f"file '{line}'\n")

    def merge(self):
        sp.call(f'ffmpeg -y -f concat -safe 0 -i "{self.host_folder}/list.txt" -c copy "{self.host_folder}.mkv"', shell=True, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        os.remove(f"{self.host_folder}/list.txt")

    def __str__(self):
        return self.host_folder


def main():
    for f in list("file", ".", ["log", "jpg"], True):
        os.remove(f)

    folders = [item for item in list("folder", ".", [], False) if re.search(r"^\d{10}$", item)]
    for folder in folders:
        date = f"{folder[:4]}_{folder[4:6]}_{folder[6:8]}"
        os.makedirs(date, exist_ok=True)
        shutil.move(folder, date)

    footages = [item for item in list("folder", ".", [], False) if re.search(r"\d{4}_\d{2}_\d{2}", item)]

    for footage in footages:
        print(f"{BCOLOR.OKBLUE}=== Processing {footage} ==={BCOLOR.ENDC}")
        f = Footage(footage)
        if not os.path.exists(f"{f.host_folder}/list.txt"):
            print(f"{BCOLOR.WARNING}Checking for corrupt files...{BCOLOR.ENDC}")
            f.checkCorrupt()
            print(f"{BCOLOR.WARNING}Writing list...{BCOLOR.ENDC}")
            f.writeList()
        print(f"{BCOLOR.WARNING}Merging...{BCOLOR.ENDC}")
        f.merge()
        shutil.rmtree(f.host_folder)
        del f

if __name__ == "__main__":
    main()
