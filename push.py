import os
import re
import sys
import math
import random
import string
import shutil
import platform
import subprocess as sp
from pkg.ffmpeg_bar import ffmpeg_bar
from pkg.BCOLORS import BCOLORS

MAX_SIZE_PER_PUSH = 100 * 1024 * 1024  # DO NOT GO BEYOND 4.88 GB
MAX_SIZE_PER_REPO = 9 * 1024 * 1024 * 1024  # 9.5 GB
HLS_SPLIT_DURATION = 10  # How small each film segment should be in seconds

FFMPEG_BINARY = "ffmpeg"
FFPROBE_BINARY = "ffprobe"

GIT_WINDOWS_PATH = "git"
GIT_LINUX_PATH = "git"

if "wsl2" in platform.platform().lower():
    GIT_WINDOWS_PATH = "git.exe"
    FFPROBE_BINARY = "ffprobe.exe"
    FFMPEG_BINARY = "ffmpeg.exe"

# =======================
# region: COSMETIC STUFFS
# =======================


def printSign(msg: str, color: str) -> None:
    msglen = len(msg) + 4
    print(color + "╔" + "═" * msglen + "╗")
    print("║  " + msg + "  ║")
    print("╚" + "═" * msglen + "╝" + BCOLORS.END)


def cls():
    sp.run('cls' if os.name == 'nt' else 'clear')

# endregion

# =================
# FUNCTIONAL STUFFS
# =================


def normalizePath(path: str) -> str:
    return os.path.normpath(path).replace("\\", "/")


def isInPath(program: str) -> bool:
    return shutil.which(program) is not None


def list(type: str, path: str, ext: list) -> list:
    results = []
    for elem in os.listdir(path):
        if type == "file":
            if os.path.isfile(os.path.join(path, elem)):
                if os.path.splitext(elem)[1].lower() in ext:
                    results.append(normalizePath(os.path.join(path, elem)))
        elif type == "dir":
            if os.path.isdir(os.path.join(path, elem)):
                results.append(normalizePath(os.path.join(path, elem)))
    return results


def getUserInputNumber(prompt: str, default: int = 1) -> int:
    option = input(prompt)
    while True:
        try:
            if option == "":
                option = default
                break
            option = int(option)
            break
        except:
            option = input(f"{BCOLORS.RED}Input must be a number: {BCOLORS.END}")
    return option


def getUserInputOption(options: list, default: int = 1) -> str:
    for i, option in enumerate(options):
        print(f"{BCOLORS.YELLOW}[{i + 1}]{BCOLORS.END} {option}")
    option = input("Enter your choice: ")
    while True:
        try:
            if option == "":
                option = default
                break
            if int(option) > len(options):
                option = input(f"{BCOLORS.RED}Input must be between 1 and {len(options)}: {BCOLORS.END}")
                continue
            option = int(option)
            break
        except:
            option = input(f"{BCOLORS.RED}Input must be an integer: {BCOLORS.END}")
    return options[option - 1]


def generateRandomAlphanumeric(length: int) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


class PushToRepo():
    def __init__(self, parts_folder: str, repo_folder: str) -> None:
        self.parts_folder = parts_folder
        self.repo_folder = repo_folder

    def __push(self) -> None:
        os.chdir(self.repo_folder)
        sp.run([GIT_WINDOWS_PATH, "add", "*"])
        sp.run([GIT_WINDOWS_PATH, "commit", "-m", f"{generateRandomAlphanumeric(10)}"])
        sp.run([GIT_LINUX_PATH, "push", "-f", "origin", "main"])
        os.chdir("../")

    def pushLoop(self):
        os.chdir(self.repo_folder)
        sp.run([GIT_WINDOWS_PATH, "config", "--add", "core.BigFileThreshold", "0"])
        os.chdir("../")

        if os.path.exists(os.path.join(self.parts_folder, "index.m3u8")):
            shutil.move(os.path.join(self.parts_folder, "index.m3u8"), self.repo_folder)

        while len(list("file", self.parts_folder, [".ts"])) > 0:
            size_limit_counter = 0
            for part in list("file", self.parts_folder, [".ts"]):
                size_limit_counter += os.path.getsize(part)
                if size_limit_counter > MAX_SIZE_PER_PUSH:
                    break
                shutil.move(part, self.repo_folder)
            self.__push()

            num_of_files_in_parts = len(list("file", self.parts_folder, [".ts"]))
            num_of_files_in_repo = len(list("file", self.repo_folder, [".ts"]))
            all_files = num_of_files_in_parts + num_of_files_in_repo
            # print progress
            _number = f"{num_of_files_in_repo} / {all_files}"
            _bar = f"[{'=' * int(num_of_files_in_repo / all_files * 20)}{' ' * (20 - int(num_of_files_in_repo / all_files * 20))}]"
            _percentage = f"{int(num_of_files_in_repo / all_files * 100)}%"
            print(f" {_number} {_bar} {_percentage}")


def main():
    cls()
    if not isInPath(FFMPEG_BINARY) or not isInPath(FFPROBE_BINARY):
        print(f"{BCOLORS.RED}ffmpeg and/or ffprobe not found in PATH{BCOLORS.END}")
        sys.exit(1)
    if not isInPath("git"):
        print(f"{BCOLORS.RED}git not found in PATH{BCOLORS.END}")
        sys.exit(1)

    printSign("Config", BCOLORS.CYAN)
    lastMsg = ""
    while True:
        cls()
        print(lastMsg) if lastMsg != "" else None
        printSign("Main menu", BCOLORS.CYAN)

        print(f"{BCOLORS.YELLOW}[1]{BCOLORS.END} Split a movie")
        print(f"{BCOLORS.YELLOW}[2]{BCOLORS.END} Clone a repo")
        print(f"{BCOLORS.YELLOW}[3]{BCOLORS.END} Push to a repo")
        print(f"{BCOLORS.YELLOW}[4]{BCOLORS.END} Change global username and email")
        print(f"{BCOLORS.YELLOW}[5]{BCOLORS.END} Exit")

        choice = ""
        while True:
            choice = input("Enter your choice: ")
            if choice in ["1", "2", "3", "4", "5"]:
                break
            printSign(f"Invalid choice", BCOLORS.RED)

        if choice == "5":
            return

        if choice == "1":
            # ----------------- Select film -----------------
            movie_path = ""
            cls()
            printSign("What movie file do you want to split?", BCOLORS.CYAN)
            available_movies = list("file", ".", [".mp4", ".mkv"])
            if len(available_movies) == 0:
                print(f"{BCOLORS.RED}No movie file found in current directory{BCOLORS.END}")
                continue
            movie_path = getUserInputOption(available_movies)

            # ----------------- Split film -----------------
            cls()
            print(f"{BCOLORS.YELLOW}Selected movie: {BCOLORS.END}{movie_path}")
            printSign("Splitting movie", BCOLORS.CYAN)
            splitted_movie_dir = "parts_" + re.sub(r"[^a-zA-Z0-9]", "_", movie_path)
            os.makedirs(splitted_movie_dir, exist_ok=True)
            os.rename(movie_path, os.path.join(splitted_movie_dir, movie_path))
            os.chdir(splitted_movie_dir)

            ffmpeg_params = ["-i", movie_path, "-map", "0:v:0", "-map", "0:a:0", "-c", "copy", "-start_number", "0", "-hls_time", str(HLS_SPLIT_DURATION), "-hls_list_size", "0", "-hls_segment_filename", "%03d.ts", "-f", "hls", "index.m3u8"]

            progress = ffmpeg_bar(ffmpeg_params, FFMPEG_BINARY, FFPROBE_BINARY)
            progress.start()
            shutil.move(movie_path, "../")
            os.chdir("../")

            if os.path.getsize(movie_path) > MAX_SIZE_PER_REPO:
                numbers_of_parts = math.ceil(os.path.getsize(movie_path) / MAX_SIZE_PER_REPO)
                for i in range(1, numbers_of_parts+1):
                    os.makedirs(f"{i}_{splitted_movie_dir}", exist_ok=True)
                part_list = list("file", splitted_movie_dir, [".ts"])

                size_limit_counter = 0
                current_part = 1
                for i, part in enumerate(part_list):
                    size_limit_counter += os.path.getsize(part)
                    if size_limit_counter > MAX_SIZE_PER_REPO:
                        current_part += 1
                        size_limit_counter = 0
                    shutil.move(part, f"{current_part}_{splitted_movie_dir}")

                shutil.move(os.path.join(splitted_movie_dir, "index.m3u8"), f"1_{splitted_movie_dir}")
                if not os.path.exists(os.path.join(splitted_movie_dir, movie_path)):
                    shutil.rmtree(splitted_movie_dir)

        if choice == "2":
            # ----------------- Clone repo -----------------
            cls()
            printSign("Config repo", BCOLORS.CYAN)
            numbers_of_repo = getUserInputNumber(f"{BCOLORS.YELLOW}How many repo do you want to clone?{BCOLORS.END} (default: 1) ")
            repo_url_list = []
            for i in range(numbers_of_repo):
                repo_url_list.append(input(f"Enter repo url {i+1}: "))
            for repo_url in repo_url_list:
                repo_folder_name = re.sub(r"[^a-zA-Z0-9]", "_", repo_url.split("/")[-1])
                sp.run([GIT_WINDOWS_PATH, "clone", repo_url, repo_folder_name])

        if choice == "3":
            numbers_of_parts = getUserInputNumber(f"{BCOLORS.YELLOW}How many part do you want to push?{BCOLORS.END} (default: 1) ")
            pair_list = []

            # let user select pair(s) of parts folder and repo folder, remove the option when it's already selected
            all_folder_list = list("dir", ".", "")
            all_repo_folder = [f for f in all_folder_list if os.path.exists(os.path.join(f, ".git"))]
            all_parts_folder = [f for f in all_folder_list if f not in all_repo_folder]
            for i in range(numbers_of_parts):
                print(f"{BCOLORS.BLUE}\nPart {i+1}{BCOLORS.END}")
                print(f"{BCOLORS.YELLOW}Select parts folder{BCOLORS.END}")
                parts_folder = getUserInputOption(all_parts_folder)
                all_parts_folder.remove(parts_folder) if parts_folder in all_parts_folder else None

                print(f"{BCOLORS.YELLOW}Select repo folder{BCOLORS.END}")
                repo_folder = getUserInputOption(all_repo_folder)
                all_repo_folder.remove(repo_folder) if repo_folder in all_repo_folder else None
                pair_list.append((parts_folder, repo_folder))

            for parts_folder, repo_folder in pair_list:
                ActionObject = PushToRepo(parts_folder, repo_folder)
                ActionObject.pushLoop()
                del ActionObject
        if choice == "4":
            user_name = input(f"{BCOLORS.YELLOW}Enter your name: {BCOLORS.END}")
            user_email = input(f"{BCOLORS.YELLOW}Enter your email: {BCOLORS.END}")
            sp.run([GIT_WINDOWS_PATH, "config", "--global", "user.name", user_name])
            sp.run([GIT_WINDOWS_PATH, "config", "--global", "user.email", user_email])

        if os.path.exists("wscript.exe") and os.path.exists("/mnt/d/sound.vbs"):
            sp.run(["wscript.exe", "D:\\sound.vbs"])

if __name__ == '__main__':
    main()
