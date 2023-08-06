import os
from argparse import ArgumentParser
from concurrent.futures import ProcessPoolExecutor, as_completed
from os import chdir, listdir
from subprocess import run

THREADS = 4


def get_args():
    parser = ArgumentParser(description="Batch compress data in folder(s) into archive(s)")
    parser.add_argument(
        "-f",
        "--format",
        help="Select the compression format [.7z (default) or .zip]",
        type=str,
        default=".7z",
        choices=[".7z", ".zip"],
    )
    parser.add_argument(
        "-e",
        "--extension",
        help="Select the file types will be compressed, each seperated by a space [txt docx ...] or [* (default)]",
        type=str,
        default="all",
    )
    return parser.parse_args()


def list_folders(path):
    return [f for f in listdir(path) if not os.path.isfile(os.path.join(path, f))]


def compress(path, format, ext_list):
    if len(listdir(path)) == 0:
        return False
    chdir(path)

    _7_zip_cmd = f'7z.exe a -bt -t{format[1:]} -x"!*.ini" -r "{os.path.join("..", f"{path}{format}")}"'

    exts = ext_list.split(" ")
    if exts[0] == "all":
        _7_zip_cmd += " *"
    else:
        for ext in exts:
            _7_zip_cmd += f" *.{ext}"
    try:
        # 7z extra params: -m0=lzma2:d1024m -mx=9 -mfb=64 -md=32m -ms=on
        run(_7_zip_cmd, shell=True, check=True)
        chdir("..")
        return True
    except:
        chdir("..")
        return False


def main():
    args = get_args()
    folders = list_folders(".")
    failed_jobs = []
    with ProcessPoolExecutor(max_workers=THREADS) as executor:
        jobs = {executor.submit(compress, folder, args.format, args.extension): folder for folder in folders}
        for job in as_completed(jobs):
            if job.result():
                print(f"\n==> SUCCESS: {jobs[job]}")
            else:
                print(f"\n==> FAILED: {jobs[job]}")
                failed_jobs.append(jobs[job])
    if len(failed_jobs) > 0:
        print(f"\n==> FAILED: {job}" for job in failed_jobs)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
    input("\nPress enter to exit...")
