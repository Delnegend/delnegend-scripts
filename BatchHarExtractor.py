import glob
import os
import re
import concurrent.futures

def main():
  for elem in glob.glob("*.har"):
    folder_path = re.sub(r'\.har',"",elem)
    compress_command = f'har-extractor.cmd "{elem}" --output "{folder_path}"'
    # create 4 concurrent compress_command
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(os.system, [compress_command])

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
    exit()