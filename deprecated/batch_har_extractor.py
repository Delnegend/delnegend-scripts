import os
import re
from concurrent.futures import ProcessPoolExecutor

import pkg.list

THREADS = 4


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
