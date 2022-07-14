import os
from argparse import ArgumentParser
from shutil import copyfile
from cv2 import resize
import subprocess as sp
import time
from dngnd import list_files, dimension, htime, THREADS
from concurrent.futures import ProcessPoolExecutor, as_completed


def get_args():
    parser = ArgumentParser("Batch upscale")
    parser.add_argument("-force_srgan", help="Force to use RealESRGAN on all images", action="store_true")
    parser.add_argument("-exit", help="Exit on complete, no confirmation", action="store_true")
    parser.add_argument("--i", help="Set input folder [.]", type=str, default=".")
    parser.add_argument("--o", help="Set output folder [./output_upscaled]", type=str, default="./output_upscaled")
    parser.add_argument("--dim", help="Set maximum output dimension [2500]", type=int, default=2500)
    parser.add_argument("--side", help="Select which side to resize [width (default), height, auto]", type=str, default="width", choices=["width", "height", "auto"])
    parser.add_argument("--thread", help="Set the number of parallel run [# of cores]", type=int, default=THREADS)
    parser.add_argument("--shelp", help="Show realesrgan help", action="store_true")
    parser.add_argument("--srgan_args", help="Add realesrgan arguments", type=str, default="")
    return parser.parse_args()


def resize(file, args):
    target_dim = args.dim
    output = args.o
    force_srgan = args.force_srgan
    extra_args = args.srgan_args
    side = args.side

    height, width, _ = dimension(file)
    if height == 0 or width == 0:
        return False
    if side == "auto":
        src_dim = max(width, height)
    elif side == "width":
        src_dim = width
    else:
        src_dim = height
    try:
        # ratio
        if (target_dim < src_dim) or (src_dim*2 >= target_dim):
            ratio = 2
        elif src_dim*3 >= target_dim:
            ratio = 3
        else:
            ratio = 4
        # upscale
        realsrgan_cmd = f'realesrgan-ncnn-vulkan -i "{file}" -o "{file}.upscaled.png" -s {str(ratio)}'
        realsrgan_cmd += " " + extra_args if extra_args else ""
        if (src_dim < target_dim) or force_srgan: # only upscale if source smaller than target or force_srgan is set
            sp.run(realsrgan_cmd, shell=True, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        else:
            copyfile(file, file + ".upscaled.png") # COPY, NOT MOVE

        # resize
        if src_dim*ratio <= target_dim: # no need to resize when the result dimension is smaller than the target
            os.rename(file + ".upscaled.png", file+".res.png")
        else:
            if src_dim == width:
                ffmpeg_resize = f'ffmpeg -i "{file}.upscaled.png" -vf "scale=\'min({target_dim},iw)\':-1" "{file}.res.png"'
            elif src_dim == height:
                ffmpeg_resize = f'ffmpeg -i "{file}.upscaled.png" -vf "scale=\'-1:min({target_dim},ih)\'" "{file}.res.png"'
            sp.run(ffmpeg_resize, shell=True, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
            os.remove(f"{file}.upscaled.png")

        # move file to output folder but keep folder structure
        out_dir = os.path.join(output, os.path.dirname(file))
        os.makedirs(out_dir, exist_ok=True)
        os.rename(f"{file}.res.png", os.path.join(out_dir, os.path.splitext(os.path.basename(file))[0] + ".png"))
        return True
    except Exception as e:
        print(e)
        return False

failed_files = []

def main(args):
    if args.shelp:
        sp.run("realesrgan-ncnn-vulkan -h", shell=True)
        return
    if not os.path.isdir(args.i):
        print("Input folder not found")
        return
    os.makedirs(args.o, exist_ok=True)
    if args.dim <= 0:
        print("Invalid dimension")
        return
    os.makedirs(args.o, exist_ok=True)
    os.chdir(args.i)
    files = list_files(".", [".png", ".jpg", ".webp"], True)
    start_time = time.time()
    with ProcessPoolExecutor(max_workers=args.thread) as executer:
        tasks = {executer.submit(resize, f, args): f for f in files}
        for task in as_completed(tasks):
            file = tasks[task]
            try:
                print("==> SUCCESS: " + file) if task.result() else None
            except:
                print("==> FAILED: " + file)
                failed_files.append(file)

    print(f"\n==> {len(files)-len(failed_files)} file(s) resized successfully in {htime(time.time()-start_time)}")

    if len(failed_files) > 0:
        print(f"\n==> Failed {len(failed_files)} file(s):")
        print(f for f in failed_files)


if __name__ == '__main__':
    args = get_args()
    try:
        main(args)
    except Exception as e:
        print(e)
    if args.exit:
        exit(1) if len(failed_files) > 0 else exit(0)
    input("\nPress enter to exit...")
