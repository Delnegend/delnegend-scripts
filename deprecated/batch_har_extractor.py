import os
import re
import shutil
from concurrent.futures import ProcessPoolExecutor

import pkg.list

THREADS = 4

if shutil.which("har-extractor.cmd") is None:
    print("Error: har-extractor.cmd not found in PATH")
    exit(1)


def main():
    for file in pkg.list.file(".", [".har"], True):
        re.sub(r"\.har$", "", file)
        with ProcessPoolExecutor(max_workers=THREADS) as executor:
            executor.submit(os.system, 'har-extractor.cmd "{file}" --output "{folder_name}"')


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
    input("\nPress enter to exit...")
