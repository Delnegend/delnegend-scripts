import os
import shutil
from dngnd import *
from subprocess import call, check_output
from argparse import ArgumentParser


def get_args():
    parser = ArgumentParser("Upscale animation")
    parser.add_argument("-i", "--input", help="Specify input file", type=str, required=True)
    parser.add_argument("-o", "--output", help="Specify output file, available format: avif, mp4, mkv", type=str, required=True)
    parser.add_argument("-e", "--encoder", help="Specify encoder for mp4/mkv [libx264 (default), libx265,...]", type=str, default="libx264")
    parser.add_argument("-crf", "--crf", help="Specify qp for mp4/mkv[0-51, default: 0]", type=int, default=0)
    return parser.parse_args()


def curr_path():
    return os.path.dirname(os.path.realpath(__file__))


def main(args):
    main_folder = os.getcwd()
    frame_rate = check_output(f'ffprobe -v error -select_streams v -of default=noprint_wrappers=1:nokey=1 -show_entries stream=r_frame_rate "{args.input}"', shell=True).decode("utf-8").strip().split("/")[0]

    # create folders
    frames = os.path.join(main_folder, os.path.basename(args.input) + "_frames")
    upscaled = os.path.join(main_folder, os.path.basename(args.input) + "_upscaled")
    os.mkdir(frames) if not os.path.exists(frames) else None
    os.mkdir(upscaled) if not os.path.exists(upscaled) else None
    # extract
    call(f'ffmpeg -i "{args.input}" -vf "fps={frame_rate}" "{frames}/%04d.png"', shell=True)
    # upscale
    os.chdir(frames)
    call(f'python "{curr_path()}/BatchResize.py" --i "{frames}" --o "{upscaled}" --dim "1080" --side "height" -exit', shell=True)
    # merge
    os.chdir(upscaled)
    call(f'ffmpeg -r {frame_rate} -i "{os.path.join(upscaled, "%04d.png")}" -c:v copy result.mkv')
    # remove frames folder
    os.chdir(main_folder)
    shutil.rmtree(frames)
    # convert to desired output format
    output_file = os.path.join(main_folder, args.output)
    os.chdir(upscaled)
    if args.output.endswith(".avif"):
        for f in list_files(".", ".png", True):
            os.remove(f)
        call("BatchAVIF", shell=True)
        os.rename("result.avif", output_file)
    else:
        call(f'ffmpeg -i result.mkv -c:v {args.encoder} -crf {args.qp} "{output_file}"', shell=True)
        # os.rename("result.mp4", output_file)
    os.chdir(main_folder)
    # remove upscaled folder
    os.remove(upscaled)
if __name__ == "__main__":
    args = get_args()
    try:
        main(args)
    except Exception as e:
        print(e)
    input("Press enter to exit")
