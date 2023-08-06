import os
import re
import shutil
import subprocess as sp
from concurrent.futures import ProcessPoolExecutor, as_completed

FFMPEG = "/media/HDD/Apps/ffmpeg"


def norm(path: str) -> str:
    return os.path.normpath(path).replace("\\", "/")


def list_files(path: str, ext: list[str], recursive: bool) -> list[str]:
    """
    path: path to the folder
    ext: list of extensions to filter, e.g. ["mp4", "jpg"]
    recursive: True or False
    """
    files: list[str] = []
    for root, _, filenames in os.walk(path):
        for filename in filenames:
            if os.path.splitext(filename)[-1].lower() in ext:
                files.append(os.path.join(root, filename))
        if not recursive:
            break
    return files


class BCOLOR:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    END = "\033[0m"


class Footage(object):
    """
    Input: a folder name in YYYY_MM_DD format
    Output: YYYY_MM_DD.mkv
    """

    def __init__(self, host_folder: str):
        if not re.search(r"\d{4}_\d{2}_\d{2}", host_folder):
            raise Exception(f"{host_folder} is not a valid date name")
        self.parts: list[str] = []
        self.host_folder = host_folder
        for item in list_files(self.host_folder, [".mp4"], True):
            self.parts.append(item)
        self.parts.sort(key=lambda x: int(x.split("_")[-1].split(".")[0]))

    def is_corrupt_single(self, file: str) -> tuple[bool, str]:
        """
        Input: a file name
        Output: (True, file) if corrupt, (False, "") if not corrupt
        """
        sp.run(f'{FFMPEG} -y -i "{file}" -t 2 -r 0.5 "{file}.jpg"', shell=True, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        if os.path.exists(f"{file}.jpg"):
            os.remove(f"{file}.jpg")
            return False, ""
        return True, file

    def is_corrupt_batch(self) -> list[str]:
        corrupted: list[str] = []
        with ProcessPoolExecutor(max_workers=8) as executor:
            tasks = [executor.submit(self.is_corrupt_single, file) for file in self.parts]
            for future in as_completed(tasks):
                is_corrupt, file = future.result()
                if is_corrupt:
                    corrupted.append(file)
        return corrupted

    def write_list(self):
        with open(f"{self.host_folder}/list.txt", "w") as file:
            file.write("")
        for line in self.parts:
            line = line.replace(f"{self.host_folder}/", "")
            with open(f"{self.host_folder}/list.txt", "a") as file:
                file.write(f"file '{line}'\n")

    def start(self):
        print(f"{BCOLOR.GREEN}=== Processing {self.host_folder} ==={BCOLOR.END}")
        for f in list_files(self.host_folder, [".log", ".jpg"], True):
            os.remove(f)

        print("  Checking for corrupt files...")
        if corrupted_files := self.is_corrupt_batch():
            for file in corrupted_files:
                print("    " + file)
                os.remove(file)

        print("  Writing list.txt for ffmpeg...")
        self.write_list()

        print("  Merging...")
        ffmpeg_data = os.path.join(self.host_folder, "list.txt")
        command = f'{FFMPEG} -y -f concat -safe 0 -i "{ffmpeg_data}" -c copy "{self.host_folder}.mkv"'
        sp.call(command, shell=True, stdout=sp.DEVNULL, stderr=sp.DEVNULL)

    def __str__(self):
        return self.host_folder


class MainMenu:
    def __init__(self, menu: dict[str, str]):
        self.menu = menu
        for key, value in menu.items():
            print(f"{BCOLOR.YELLOW}[{key}] {value}{BCOLOR.END}")

    # ----- HELPERS -----

    def get_choice(self) -> int:
        choice = input(f"{BCOLOR.BLUE}Your choice: {BCOLOR.END}")
        while True:
            if choice.isdigit():
                if int(choice) in range(1, len(self.menu) + 1):
                    return int(choice)
            choice = input(f"{BCOLOR.RED}Invalid choice, try again: {BCOLOR.END}")

    def preparing_folders(self) -> None:
        hostdirs: list[str] = []
        for folder in [
            item for item in [i for i in os.listdir(".") if os.path.isdir(i)] if re.search(r"^\d{10}$", item)
        ]:
            hostdir = f"{folder[:4]}_{folder[4:6]}_{folder[6:8]}"
            hostdirs.append(hostdir) if hostdir not in hostdirs else None
            os.mkdir(hostdir) if not os.path.exists(hostdir) else None

        for folder in [
            item for item in [i for i in os.listdir(".") if os.path.isdir(i)] if re.search(r"^\d{4}_\d{2}_\d{2}$", item)
        ]:
            hostdirs.append(folder) if folder not in hostdirs else None

        hostdirs.sort()
        hostdirs.pop()

        for folder in hostdirs:
            print("  " + folder)
        if input("These are the folders to process, continue? (y/n): ") != "y":
            return

        for folder in [i for i in os.listdir(".") if os.path.isdir(i) and re.search(r"^\d{10}$", i)]:
            hostdir = f"{folder[:4]}_{folder[4:6]}_{folder[6:8]}"
            shutil.move(folder, hostdir) if hostdir in hostdirs else None

        self.hostdirs = hostdirs

    def select_hostdir(self) -> str:
        print(f"{BCOLOR.GREEN}=== Select a folder ==={BCOLOR.END}")

        for i, folder in enumerate(self.hostdirs):
            print(f"{BCOLOR.GREEN}{i + 1}. {folder}{BCOLOR.END}")
        host_idx_select = input("Your choice: ")
        while True:
            host_idx_select = input(f"{BCOLOR.BLUE}Your choice: {BCOLOR.END}")
            if not host_idx_select.isdigit():
                print(f"{BCOLOR.RED}Invalid choice{BCOLOR.END}")
                continue
            if int(host_idx_select) not in range(1, len(self.hostdirs) + 1):
                print(f"{BCOLOR.RED}Invalid choice{BCOLOR.END}")
                continue
            seleted_host_folder = str(self.hostdirs[int(host_idx_select) - 1])
            break
        return seleted_host_folder

    # ----- MENU -----

    def auto_pilot(self) -> None:
        for folder in [i for i in os.listdir(".") if os.path.isdir(i) and re.search(r"^\d{4}_\d{2}_\d{2}$", i)]:
            footage = Footage(folder)
            footage.start()
            shutil.rmtree(folder)

    def merge_one(self) -> None:
        selected_hostdir = self.select_hostdir()
        footage = Footage(selected_hostdir)
        footage.start()
        shutil.rmtree(selected_hostdir)

    def check_corrupt(self) -> None:
        selected_hostdir = self.select_hostdir()
        footage = Footage(selected_hostdir)
        corrupted_files = footage.is_corrupt_batch()
        if corrupted_files:
            print(f"{BCOLOR.YELLOW}Corrupted files:{BCOLOR.END}")
            for file in corrupted_files:
                print(BCOLOR.YELLOW + file + BCOLOR.END)
            return
        print(f"{BCOLOR.GREEN}No corrupted files{BCOLOR.END}")

    def preview_list(self) -> None:
        selected_hostdir = self.select_hostdir()
        footage = Footage(selected_hostdir)
        footage.write_list()
        with open(f"{selected_hostdir}/list.txt", "r") as file:
            print(file.read())


def main():
    for file in list_files(".", [".log", ".jpg"], True):
        os.remove(file)
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        menu = MainMenu(
            {
                "1": "Autopilot (auto clean, detect, merge)",
                "2": "Merge only one date",
                "3": "Check for corrupt files of one date",
                "4": "Preview the list of one date",
                "5": "Exit",
            }
        )
        menu.preparing_folders()
        choice = menu.get_choice()
        match choice:
            case 1:
                menu.auto_pilot()
            case 2:
                menu.merge_one()
            case 3:
                menu.check_corrupt()
            case 4:
                menu.preview_list()
            case 5:
                break
            case _:
                pass

        input("Press Enter to continue...")


if __name__ == "__main__":
    if os.name == "posix" and os.geteuid() != 0:
        print(f"{BCOLOR.RED}Please run as root{BCOLOR.END}")
        exit(1)

    if not os.path.exists(FFMPEG):
        print(f"{BCOLOR.RED}FFMPEG not found at {FFMPEG}{BCOLOR.END}")
        exit(1)
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nKeyboardInterrupt")
