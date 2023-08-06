import os
import shutil
import sys
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from subprocess import PIPE, run
from time import time

import pkg

THREADS = 4

config = {
    "image": {
        "format": [".png", ".jpeg", ".jpg", ".tiff", ".tif", ".bmp"],
        "extractor": "ffmpeg -i {{ input }} -strict -2 -pix_fmt yuv444p10le -f yuv4mpegpipe -y {{ output }}",
        "encoder": "aomenc --codec=av1 --allintra --i444 --threads={{ threads }} --bit-depth=10 --max-q=63 --min-q=0 --end-usage=q --cq-level=25 --cpu-used=6 --enable-chroma-deltaq=1 --qm-min=0 --aq-mode=1 --deltaq-mode=3 --sharpness=2 --enable-dnl-denoising=0 --denoise-noise-level=5 --tune=ssim --width={{ width }} --height={{ height }} {{ input }} --ivf -o {{ output }}",
        "fallback": "",
        "repackager": "MP4Box -add-image {{ input }}:primary -ab avif -ab miaf -new {{ output }}",
    },
    "animation": {
        "format": [".gif", ".mp4", ".webm"],
        "extractor": "ffmpeg -i {{ input }} -strict -2 -pix_fmt yuv444p10le -f yuv4mpegpipe -y {{ output }}",
        "encoder": "aomenc --codec=av1 -i444 --threads={{ threads }} --bit-depth=10 --max-q=63 --min-q=0 --end-usage=q --cq-level=18 --cpu-used=6 --enable-chroma-deltaq=1 --qm-min=0 --aq-mode=1 --enable-dnl-denoising=0 --denoise-noise-level=5 --tune=ssim --width={{ width }} --height={{ height }} {{ input }} --ivf -o {{ output }}",
        "fallback": "",
        "repackager": "ffmpeg -i {{ input }} -c copy -map 0 -brand avis -f mp4 {{ output }}",
    },
    "threads": 1,
    # 'mode': 'file',
    "del_after_convert": False,
    "keep_original_extension": False,
    "overwrite": False,
    "log": False,
}


def get_args():
    parser = ArgumentParser(description="AVIF batch encoder.")
    parser.add_argument(
        "-i",
        "--input",
        help="Input directory",
        default=os.getcwd(),
        type=str,
        required=False,
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output directory",
        default="./avif_output",
        type=str,
        required=False,
    )
    parser.add_argument("-exit", help="Exit right after conversion", action="store_true", required=False)
    parser.add_argument(
        "-no_success",
        help="Don't print success messages",
        action="store_true",
        required=False,
    )
    return parser.parse_args()


def parse_presets(file, ext, enc, rep):
    name = file if config["keep_original_extension"] else os.path.splitext(file)[0]
    ext = ext.replace("{{ input }}", f'"{file}"')
    ext = ext.replace("{{ output }}", f'"{file}.y4m"')
    enc = enc.replace("{{ input }}", f'"{file}.y4m"')
    enc = enc.replace("{{ output }}", f'"{file}.ivf"')
    enc = enc.replace("{{ threads }}", f"{THREADS}")
    rep = rep.replace("{{ input }}", f'"{file}.ivf"')
    rep = rep.replace("{{ output }}", f'"{name}.avif"')
    return name, ext, enc, rep


def execCmd(cmd: str, log: str):
    command = run(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    if log is not None:
        with open(log, "a") as f:
            f.write(f"EXEC: {cmd}\n")
            f.write(f'{datetime.now()}: {command.stdout.decode("utf-8")}\n')
            f.write(f'{datetime.now()}: {command.stderr.decode("utf-8")}\n')
    return command.returncode


def convert(
    file: str,
    ext_: str,
    enc_: str,
    fallback_: str,
    repack_: str,
    log: str,
    detailed: bool,
):
    name, ext, enc, repack = parse_presets(file, ext_, enc_, repack_)
    print(f"==> {file}", end=" ") if detailed else None
    if execCmd(ext, log) != 0:
        os.remove(f"{file}.y4m") if os.path.exists(f"{file}.y4m") else None
        print("failed to extract") if detailed else None
        return file

    # getting dimension after extracting to raw frame(s) to avoid dimension mismatch
    if "{{ width }}" in enc or "{{ height }}" in enc:
        w, h = pkg.dimension(file)
        enc = enc.replace("{{ width }}", str(w))
        enc = enc.replace("{{ height }}", str(h))

    if execCmd(enc, log) != 0 and fallback_ == "":
        os.remove(f"{file}.y4m") if os.path.exist(f"{file}.y4m") else None
        os.remove(f"{file}.ivf") if os.path.exist(f"{file}.ivf") else None
        print("failed to encode") if detailed else None
        return file
    elif fallback_ != "":
        os.remove(f"{file}.ivf")
        fallback = fallback_.replace("{{ input }}", f'"{file}.y4m"')
        fallback = fallback.replace("{{ output }}", f'"{file}.ivf"')
        if execCmd(fallback, log) != 0:
            os.remove(f"{file}.y4m") if os.path.exists(f"{file}.y4m") else None
            os.remove(f"{file}.ivf") if os.path.exists(f"{file}.ivf") else None
            print("failed to fallback") if detailed else None
            return file
    if execCmd(repack, log) != 0:
        os.remove(f"{file}.y4m") if os.path.isfile(f"{file}.y4m") else None
        os.remove(f"{file}.ivf") if os.path.isfile(f"{file}.ivf") else None
        os.remove(f"{name}.avif") if os.path.isfile(f"{name}.avif") else None
        print("failed to repack") if detailed else None
        return file

    os.remove(f"{file}.y4m")
    os.remove(f"{file}.ivf")
    os.makedirs(os.path.join(args.output, os.path.dirname(file)), exist_ok=True)
    shutil.move(f"{name}.avif", os.path.join(args.output, f"{name}.avif"))
    return 0


def convert_batch(
    file_list: list,
    ext: str,
    enc: str,
    fallback: str,
    repack: str,
    stats: dict,
    log: str,
):
    if config["threads"] > 1:
        with ThreadPoolExecutor(max_workers=config["threads"]) as executor:
            futures = {
                executor.submit(convert, file, ext, enc, fallback, repack, None, False): file for file in file_list
            }
            for future in as_completed(futures):
                file = futures[future]
                if future.result() == 0:
                    name = file if config["keep_original_extension"] else os.path.splitext(file)[0]
                    original_size = os.path.getsize(file)
                    converted_size = os.path.getsize(os.path.join(args.output, f"{name}.avif"))
                    stats["original"] += original_size
                    stats["converted"] += converted_size
                    print(f"{file} converted") if not args.no_success else None
                else:
                    stats["fail"].append(file)
                    print(f"{file} failed")
    elif config["threads"] == 1:
        for file in file_list:
            name = file if config["keep_original_extension"] else os.path.splitext(file)[0]
            convert(file, ext, enc, fallback, repack, log, True)
            if convert(file, ext, enc, fallback, repack, log, True) == 0:
                original_size = os.path.getsize(file)
                converted_size = os.path.getsize(os.path.join(args.output, f"{name}.avif"))
                stats["original"] += original_size
                stats["converted"] += converted_size
                print("converted") if not args.no_success else None
            else:
                stats["fail"].append(file)
                print(f"{file} failed")


def main(args):
    stats = {
        "fail": [],
        "skip": [],
        "original": 0,
        "converted": 0,
    }

    images = pkg.list.list_file(args.input, config["image"]["format"])
    animations = pkg.list.list_file(args.input, config["animation"]["format"])
    all = images + animations

    # create log file if doesn't exist
    log = None
    if config["log"]:
        log = f'{datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.log'
        with open(log, "w") as f:
            f.write("")

    # check for duplicate filenames to avoid things like
    # A.png --> A.avif && A.jpg --> A.avif ==> error
    if config["keep_original_extension"]:

        def rmExt(path):
            return os.path.splitext(path)[0]

        files = all
        dupls = []
        for i in range(len(files)):
            for j in range(i, len(files)):
                if rmExt(files[i]) == rmExt(files[j]) and (files[i] != files[j]):
                    if files[i] in files:
                        dupls.append(files[i])
                    if files[j] in files:
                        dupls.append(files[j])
        if len(dupls) > 0:
            print("Duplicate filenames found:")
            for d in dupls:
                print(d)
            print("Please remove them before running this script.")
            sys.exit(1)

    if config["del_after_convert"]:
        input("WARNING: This will delete all files in the input directory. Press Enter to continue.")

    if config["overwrite"]:
        input("WARNING: This will overwrite all converted in the output directory. Press Enter to continue.")
        for f in all:
            stats["skip"].append(f)
            name = os.path.splitext(f)[0] if config["keep_original_extension"] else f
            os.remove(f"{name}.avif")

    # get current time
    start_timer = time()

    convert_batch(
        images,
        config["image"]["extractor"],
        config["image"]["encoder"],
        config["image"]["fallback"],
        config["image"]["repackager"],
        stats,
        log,
    )
    convert_batch(
        animations,
        config["animation"]["extractor"],
        config["animation"]["encoder"],
        config["animation"]["fallback"],
        config["animation"]["repackager"],
        stats,
        log,
    )

    num_of_files_converted = len(all) - len(stats["skip"]) - len(stats["fail"])
    time_taken = pkg.human_readable.time(time() - start_timer)
    print(f"{num_of_files_converted} files converted in {time_taken}")

    readable_original_size = pkg.human_readable.size(stats["original"])
    readable_converted_size = pkg.human_readable.size(stats["converted"])
    ratio = f'{round((stats["converted"]/stats["original"])*100, 2)}%'

    print(f"{readable_original_size} -> {readable_converted_size} ~ {ratio}")

    if len(stats["fail"]) > 0:
        print(f'{len(stats["fail"])} files failed to convert')
        for f in stats["fail"]:
            print(f)


if __name__ == "__main__":
    args = get_args()
    if not os.path.exists(args.input):
        print(f'Input path "{args.input}" not found', file=sys.stderr)
        sys.exit(1)
    os.makedirs(args.output, exist_ok=True)
    main(args)
