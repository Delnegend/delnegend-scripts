from socket import timeout
import subprocess as sp
import argparse
import os
import time

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, help='Input video file')
    parser.add_argument('-f', '--fast', help='Use Low-Res model for faster upscaling', action='store_true', default=False)
    return parser.parse_args()


def num_frames(folder):
    return len([name for name in os.listdir(folder) if os.path.isfile(os.path.join(folder, name))])

def secondsToStr(t):
    hour = int(t / 3600)
    min = int((t - hour * 3600) / 60)
    sec = int(t - hour * 3600 - min * 60)
    return "%d:%02d:%02d" % (hour, min, sec)

def progress_bar(total, current, begin_time):
    size = 20
    curr_time = time.time()
    elapsed = curr_time - begin_time
    eta = elapsed / current * (total - current) if current > 0 else 0
    time_finished = curr_time + eta

    # time finished in HH:MM:SS AM/PM
    time_section = f"Elapsed {secondsToStr(elapsed)} - ETA {secondsToStr(eta)} - Finished {time.strftime('%I:%M:%S %p', time.localtime(time_finished))}"
    bar_section = f"[{'=' * int(current / total * size)}{' ' * (size - int(current / total * size))}]"
    percent_section = f"{int(current / total * 100)}%"
    return f"{time_section} | {bar_section} {percent_section}"

def main(args):
    model = 'realesr-animevideov3' if args.fast else 'realesrgan-x4plus-anime'
    frames_folder = args.input+"_frames"
    upscaled_folder = args.input+"_upscaled"
    os.makedirs(frames_folder) if not os.path.exists(frames_folder) else None
    os.makedirs(upscaled_folder) if not os.path.exists(upscaled_folder) else None

    print("Extracting...", end='\r')

    sp.call(f'ffmpeg.exe -i "{args.input}" -q:v 2 "{os.path.join(frames_folder, "%05d.png")}"', shell=False, stdout=sp.DEVNULL, stderr=sp.DEVNULL)

    num_raw_frames = num_frames(frames_folder)
    print(f"Extracted {num_raw_frames} frames")

    print("Upscaling with model", model)

    upscale_process = sp.Popen(f'realesrgan-ncnn-vulkan -i "{frames_folder}" -o "{upscaled_folder}" -n {model} -f jpg', shell=True, stdout=sp.DEVNULL, stderr=sp.DEVNULL)

    # Progress bar
    begin_time = time.time()
    upscaled_frame_placeholder = 0
    while upscale_process.poll() is None:
        num_upscaled_frames = num_frames(upscaled_folder)
        if num_upscaled_frames > upscaled_frame_placeholder:
            upscaled_frame_placeholder = num_upscaled_frames
            print(progress_bar(num_raw_frames, num_upscaled_frames, begin_time), end='\r')
        time.sleep(5)
    print()
    upscale_process.wait()
    print("Done!")
    upscale_process.terminate()
    sp.call('wscript D:\sound.vbs', shell=False, stdout=sp.DEVNULL, stderr=sp.DEVNULL)


if __name__ == "__main__":
    main(parse_args())
