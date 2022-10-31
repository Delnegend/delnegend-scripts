import os
import sys
import subprocess as sp
import argparse

AVIF_CQ = 18  # 0-63, lower is better
AVIF_TUNE = 1  # PSNR (better for graphics), 1 for SSIM (better for real photos)
AVIF_PIX_FMT = "420"
JXL_DISTANCE = 1  # 0-15, lower is better
JXL_EFFORT = 9  # 1-9, higher is better
WEBP_Q = 90  # 0-100, higher is better
JPG_Q = 90  # 0-100, higher is better


def dim(img):
    raw = sp.check_output(f'ffprobe -v error -show_entries stream=width,height -of default=noprint_wrappers=1:nokey=1 {img}', stderr=sp.DEVNULL)
    processed = raw.decode("utf-8").strip().split("\r\n")
    return int(processed[0]), int(processed[1])


def inPath(name):
    return sp.call(f'where {name}', shell=True, stdout=sp.DEVNULL, stderr=sp.DEVNULL) == 0


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="input file")
    parser.add_argument("-o", "--output", help="output file")
    parser.add_argument("-max", help="Set max size (default: a10000)", default="a10000")
    parser.add_argument("-force", help="Force RealESRGAN", action="store_true")
    parser.add_argument("-format", help="Set output format, each seperated by a space, available: jpg, png (lossless), avif, jxl", type=str, default="jpg avif jxl")
    parser.add_argument("-model", help="Model of RealESRGAN (default: details)", type=str, default="details", choices=["details", "fast"])
    return parser.parse_args()


def encode(input, output, format):
    if format == "png":
        cmd = f'ffmpeg -i {input} -q:v 2 {output}.png'
        print("ffmpeg-png:", cmd)
    if format in ["jpg", "jpeg"]:
        if inPath("cjpeg-static"):
            cmd = f'cjpeg-static -q {JPG_Q} -outfile {output}.jpg {input}'
            print("cjpeg-static:", cmd)
        else:
            cmd = f'ffmpeg -i {input} -q:v 2 {output}.jpg'
            print("ffmpeg-jpg:", cmd)
    elif format == "webp":
        cmd = f'ffmpeg -i {input} -q:v 2 -c:v libwebp -quality {WEBP_Q} -compression_level 6 {output}.webp'
        print("ffmpeg-webp:", cmd)
    elif format == "avif":
        if inPath("avifenc"):
            cmd = f'avifenc -y {AVIF_PIX_FMT} -d 10 -c aom -a aq-mode=1 -a cq-level={AVIF_CQ} -a enable-chroma-deltaq=1 -a tune=ssim {input} {output}.avif'
            print("avifenc:", cmd)
        else:
            cmd = f'ffmpeg -i {input} -c:v libaom-av1 -cpu-used 6 -aq-mode 1 -pix_fmt yuv{AVIF_PIX_FMT}p10le -aom-params enable-chroma-deltaq=1:cq-level={AVIF_CQ} {output}.avif'
            print("ffmpeg-avif:", cmd)
    elif format == "jxl":
        if inPath("cjxl"):
            cmd = f'cjxl {input} {output}.jxl -d {JXL_DISTANCE} -e {JXL_EFFORT}'
            print("cjxl:", cmd)
        else:
            cmd = f'ffmpeg -i {input} -c:v libjxl -distance {JXL_DISTANCE} -effort {JXL_EFFORT} {output}.jxl'
            print("ffmpeg-jxl:", cmd)
    sp.call(cmd, shell=True, stdout=sp.DEVNULL, stderr=sp.DEVNULL)


def main(args):
    name = os.path.splitext(args.input)[0]
    width, height = dim(args.input)
    if width == 0 or height == 0:
        print("Invalid image")
        sys.exit(1)

    # ============
    # PARSE CONFIG
    # ============
    max_res = int(args.max[1:])
    mode = args.max[0] if args.max[0] in ["w", "h"] else "w" if width > height else "h"

    # =======
    # UPSCALE
    # =======
    upscaled_file = f"{name}_upscaled.png"
    if ((mode == "w") and (width < max_res)) or ((mode == "h") and (height < max_res)) or args.force:
        print("==> Upscaling...")
        scale = 2 if width*2 >= max_res and height*2 >= max_res else 3 if width*3 >= max_res and height*3 >= max_res else 4
        scale = 4 if args.model == "details" else scale
        model = "realesrgan-x4plus-anime" if args.model == "details" else "realesr-animevideov3"
        print(f"Using model {model} with scale {scale}")
        sp.call(f'realesrgan-ncnn-vulkan -n {model} -s {scale} -i {args.input} -o {upscaled_file}', shell=True, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        if mode == "w" and dim(upscaled_file)[0] > max_res:
            sp.call(f'ffmpeg -i {upscaled_file} -vf scale={max_res}:-1 {upscaled_file}_.png', shell=True, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        elif mode == "h" and dim(upscaled_file)[1] > max_res:
            sp.call(f'ffmpeg -i {upscaled_file} -vf scale=-1:{max_res} {upscaled_file}_.png', shell=True, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        os.remove(upscaled_file)
        os.rename(f"{upscaled_file}_.png", upscaled_file)

    # ======
    # ENCODE
    # ======
    print("==> Encoding...")
    # if args.output is empty || is the same as args.input => set to input.result
    output = args.output if args.output and args.output != args.input else f"{args.input}.result"
    if not os.path.splitext(output)[1]:  # if output has no extension, use the args.format list
        # convert to lowercase, replace jpeg with jpg, remove duplicates
        out_formats = list(dict.fromkeys([x.lower().replace("jpeg", "jpg") for x in args.format.split(" ")]))
        for fmt in out_formats:
            encode(upscaled_file if os.path.exists(upscaled_file) else args.input, output, fmt.lower())
    else:  # if output has an extension, only encode to that format
        encode(upscaled_file if os.path.exists(upscaled_file) else args.input, output, os.path.splitext(output)[1][1:])

    # ========
    # CLEAN UP
    # ========
    if os.path.exists(upscaled_file):
        os.remove(upscaled_file) if input("==> Remove upscaled file? y/n: ").lower() == "y" else None

    # sp.call("wscript D:\sound.vbs")


def checkBinary(name):
    if not inPath(name):
        print(f"{name} not found in PATH")
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    args = parse_args()

    if not args.input or not os.path.exists(args.input):
        print("Invalid input file")
        sys.exit(1)

    checkBinary("ffprobe")
    checkBinary("ffmpeg")
    checkBinary("realesrgan-ncnn-vulkan")
    print("For more efficient jpg encoding (mozjpeg), consider adding cjpeg-static to PATH. Ignore this if you don't encode to jpg.") if not inPath("cjpeg-static") else None

    main(args)
