import glob
import os
import re
import concurrent.futures


def list_files(path, ext):
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(ext):
                yield os.path.join(root, file)

def main():
    for file in list_files(".", ".har"):
        folder_name = re.sub(r"\.har$", "", file)
        with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
            executor.submit(os.system, 'har-extractor.cmd "{file}" --output "{folder_name}"')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
    exit()
