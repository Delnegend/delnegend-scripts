import os
import re
from concurrent.futures import ProcessPoolExecutor, as_completed
from dngnd import *


def main():
    for file in list_files(".", [".har"], True):
        folder_name = re.sub(r"\.har$", "", file)
        with ProcessPoolExecutor(max_workers=THREADS) as executor:
            executor.submit(
                os.system, 'har-extractor.cmd "{file}" --output "{folder_name}"')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
    input("\nPress enter to exit...")
