import os
import subprocess as sp
import shutil
import argparse
from pkg import print_sign, list


def curr_path():
    return os.path.dirname(os.path.realpath(__file__))


def get_args():
    parser = argparse.ArgumentParser("Batch process packs")
    parser.add_argument("-i", "--input", help="Specify main input folder", type=str, default=".")
    parser.add_argument("-force_srgan", help="Force to use RealESRGAN on all images", action="store_true")
    parser.add_argument("-m", "--mode", help="Process from JPG/PNG or JXL [raw (default), jxl]", type=str, default="raw", choices=["raw", "jxl", "webp"])
    parser.add_argument("-no_archive", help="No compressing to zip/7z, just process to jxl and avif", action="store_true")
    return parser.parse_args()


def stage_resize(main_folder, pack, args):
    # resize images
    print_sign("Resizing stage", "small")
    resize_cmd = f'python "{curr_path()}/BatchResize.py" --i "." -exit'
    resize_cmd += " -force_srgan" if args.force_srgan else ""
    sp.call(resize_cmd, shell=True)
    # move resized images to a seperated folder to convert to avif
    upscale_folder = os.path.join(main_folder, pack + "_upscaled")
    os.rename("output_upscaled", upscale_folder)
    return upscale_folder


def stage_copy_ani(upscale_folder):
    animations = list.list_file(".", [".mp4", ".mkv", ".gif", ".webm"], True)
    if len(animations) > 0:
        print_sign("Copying gif and mp4 files", "small")
        for f in animations:
            shutil.copy(f, upscale_folder)
            print(f"Copied {f}")


def stage_avif(upscale_folder, main_folder, pack, args):
    print_sign("AVIF encode stage", "small")
    os.chdir(upscale_folder)
    sp.call('BatchAVIF', shell=True)
    if not args.no_archive:
        sp.run(
            f'7z.exe a -bt -tzip -x"!*.ini" -r "{os.path.join(main_folder, pack)}.zip" *.avif',
            shell=True, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    else:
        for i in list.list_file(".", [".avif"], True):
            os.rename(i, os.path.join(main_folder, pack, i))
    os.chdir(main_folder)
    shutil.rmtree(upscale_folder)

# PNG/JPG
# --> JXL --> 7z
# --> AVIF --> resize --> zip


def from_raw(args):
    packs = list.list_folder(args.input, True)
    main_folder = os.getcwd()
    for pack in packs:
        print_sign("Processing pack: " + pack, "main")
        os.chdir(pack)

        # convert orginal to jxl and (pack to 7z + del .jxl) if args specified
        print_sign("JXL encode stage", "small")
        sp.call(f'python "{curr_path()}/BatchJXL.py" -exit --formats ".jpg .jpeg .png"', shell=True)
        if not args.no_archive:
            sp.run(
                f'7z.exe a -bt -t7z -x"!*.ini" -r "{os.path.join(main_folder, pack)}.7z" *.jxl *.mp4 *.gif',
                shell=True, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
            for file in list.list_file(".", [".jxl"], True):
                os.remove(file)

        # resize
        upscale_folder = stage_resize(main_folder, pack, args)

        # copy gif and mp4 files from pack to upscaled_folder
        stage_copy_ani(upscale_folder)

        # convert resized to avif, remove resized && (pack into zip, del upscale folder) if doesn't specify else move to main folder
        stage_avif(upscale_folder, main_folder, pack, args)

    print_sign("Done processing all packs", "main")


# JXL --> PNG --> resize --> AVIF --> zip
def from_jxl(args):
    packs = list.folder(args.input, True)
    main_folder = os.getcwd()
    for pack in packs:
        print_sign("Processing pack: " + pack, "main")
        os.chdir(pack)

        # JXL --> PNG
        print_sign("JXL decode stage", "small")
        sp.call(f'python "{curr_path()}/BatchJXL.py" -d -exit', shell=True)

        # resize
        upscale_folder = stage_resize(main_folder, pack, args)

        # remove PNG converted from JXL
        for f in list.file(".", [".png"], True):
            os.remove(f)

        # copy animations from pack to upscale_folder
        stage_copy_ani(upscale_folder)

        # images, animations --> AVIF
        stage_avif(upscale_folder, main_folder, pack, args)

        os.chdir(main_folder)
        shutil.rmtree(upscale_folder)


if __name__ == '__main__':
    try:
        args = get_args()
        if args.mode == "raw":
            from_raw(args)
        elif args.mode == "jxl":
            from_jxl(args)
    except Exception as e:
        print(e)
    input("Press enter to exit")
