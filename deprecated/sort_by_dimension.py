from pathlib import Path
from shutil import move

import pkg.dimension
import pkg.list

Path("./Portrait/").mkdir(parents=True, exist_ok=True)
Path("./Square/").mkdir(parents=True, exist_ok=True)
Path("./Landscape/").mkdir(parents=True, exist_ok=True)


def main():
    for file in pkg.list.file(".", [], recursive=True):
        try:
            width, height = pkg.dimension(file)
            if width > height:
                move(file, "./Landscape/")
            elif width < height:
                move(file, "./Portrait/")
            else:
                move(file, "./Square/")
        except:
            print("Not An Image")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
    input("\nPress enter to exit...")
