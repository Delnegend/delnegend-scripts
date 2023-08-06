import argparse
import os
import subprocess as sp
import time


def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="input media file", required=True)
    parser.add_argument("-max", help="max dimension", default="h2160")
    parser.add_argument("-model", help="fast/details", default="details", choices=["fast", "details"])
    parser.add_argument(
        "-update_freq",
        help="Change how frequent the progress bar update",
        default=3,
        type=int,
    )
    return parser.parse_args()


def Dimension(media):
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height",
        "-of",
        "csv=s=x:p=0",
        media,
    ]
    w, h = sp.check_output(cmd).decode("utf-8").split("x")
    return int(w), int(h)


def humanReadableTime(seconds):
    hour = int(seconds / 3600)
    minute = int((seconds % 3600) / 60)
    second = int(seconds % 60)
    return f"{hour:02d}:{minute:02d}:{second:02d}"


def progressBar(value, endvalue, start_time, bar_length=20):
    percent = float(value) / endvalue if endvalue else 0
    bar = (
        "["
        + "=" * int(round(percent * bar_length) - 1)
        + ">"
        + " " * (bar_length - int(round(percent * bar_length)))
        + "]"
    )
    time_taken = time.time() - start_time
    eta = (time_taken / value) * (endvalue - value) if value else 0
    # calculate when the task will be finished with AM/PM
    finish_at = time.localtime(time.time() + eta)
    return f'{bar} {percent*100:.2f}% {humanReadableTime(time_taken)} / {humanReadableTime(eta)} ({time.strftime("%I:%M:%S %p", finish_at)})'


def listFiles(path):
    import os

    return len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])


def main(args):
    # Creating folders
    frames = args.input + ".frames"
    upscale = args.input + ".upscale"
    os.makedirs(frames) if not os.path.exists(frames) else None
    os.makedirs(upscale) if not os.path.exists(upscale) else None

    # Extract frames from video
    print("Extracting frames...", end="\r")
    sp.call(
        ["ffmpeg", "-i", args.input, "-q:v", "2", os.path.join(frames, "%06d.jpg")],
        stdout=sp.DEVNULL,
        stderr=sp.DEVNULL,
    )
    frames_amount = listFiles(frames)
    print(f"Extracted {frames_amount} frames")
    # Calculate ratio for RealESRGAN
    w, h = Dimension(args.input)
    config_side = args.max[0].lower()
    source_size = h
    if (config_side == "a" and w > h) or (config_side == "w"):
        source_size = w
    ratio = 0
    if source_size * 2 >= int(args.max[1:]):
        ratio = 2
    elif source_size * 3 >= int(args.max[1:]):
        ratio = 3
    else:
        ratio = 4
    if args.model == "details":
        ratio = 4
        model = "realesrgan-x4plus-anime"
    else:
        model = "realesr-animevideov3"

    print("Upscaling frames...")
    start_time = time.time()
    proc = sp.Popen(
        [
            "realesrgan-ncnn-vulkan.exe",
            "-i",
            frames,
            "-o",
            upscale,
            "-n",
            model,
            "-s",
            str(ratio),
        ],
        stdout=sp.DEVNULL,
        stderr=sp.DEVNULL,
    )
    while True:
        print(progressBar(listFiles(upscale), frames_amount, start_time), end="\r")
        if proc.poll() is not None:
            break
        time.sleep(args.update_freq)
    print(progressBar(listFiles(upscale), frames_amount, start_time))
    proc.wait()


if __name__ == "__main__":
    main(getArgs())
