import time
import ffprobe
import subprocess as sp
import human_readable
import os
import BCOLORS

class ffmpeg_bar(object):

    def __init__(self, ffmpeg_params: list) -> None:
        self.ffmpeg_params = ffmpeg_params

    def __progress_bar(self, value, endvalue, start_time, bar_length=20):
        percent = float(value) / endvalue if endvalue else 0
        bar_fill = '=' * int(round(percent * bar_length))
        bar_empty = ' ' * (bar_length - len(bar_fill))
        bar = bar_fill + bar_empty
        time_taken = time.time() - start_time
        eta = (time_taken / value) * (endvalue - value) if value else 0
        finish_at = time.localtime(time.time() + eta)

        time_taken = human_readable.time(time_taken)
        eta = human_readable.time(eta)
        finish_at = time.strftime("%I:%M:%S %p", finish_at)

        return f'{value} / {endvalue} [{bar}] {percent*100:.2f}% {time_taken} / {eta} ({finish_at})'

    def __parse_ffmpeg_status(self, stdout):
        data = stdout.readline()
        if not data or not data.startswith('frame='):
            return None
        frame = data.split('frame=')[1].split('fps=')[0].strip()
        fps = data.split('fps=')[1].split('q=')[0].strip()
        return {'frame': frame, 'fps': fps}

    def __sign_for_log(self, message: str) -> str:
        data = "\n"
        len_message = len(message)
        data += "=" * (len_message + 6) + "\n"
        data += f"=  {message}  =\n"
        data += "=" * (len_message + 6) + "\n"
        return data

    def run(self, log: bool = False) -> None:
        fps_recored = []
        ffmpeg_params = self.ffmpeg_params

        input_file = ffmpeg_params[ffmpeg_params.index('-i') + 1]
        input_file_ffprobe = ffprobe(input_file)

        total_frame_count = int(input_file_ffprobe['streams'][0]['nb_frames'])
        start_time = time.time()

        if log:
            # create a log.txt file
            with open("log.txt", "w") as f:
                f.write(self.__sign_for_log(input_file))

        proc = sp.Popen(["ffmpeg"] + ffmpeg_params,
                        stdout=sp.PIPE,
                        stderr=sp.PIPE,
                        universal_newlines=True)

        while proc.poll() is None:
            data = self.__parse_ffmpeg_status(proc.stderr)
            if data is not None:
                if log:
                    with open("log.txt", "a") as f:
                        f.write(proc.stderr.readline())
                fps_recored.append(float(data['fps']))
                print("{}{}fps {}{}".format(
                    "\r" if os.name != 'nt' else "",
                    round(float(data['fps']), 2),
                    self.__progress_bar(int(data['frame']), total_frame_count, start_time),
                    " "*3
                ), end=("" if os.name != 'nt' else "\r"))


        avg_fps = sum(fps_recored) / len(fps_recored) if len(fps_recored) else 0
        print("{}{}fps {}{}".format(
            "\r" if os.name != 'nt' else "",
            # avg_fps,
            round(avg_fps, 2),
            self.__progress_bar(total_frame_count, total_frame_count, start_time),
            " "*3
        ))

        before = human_readable.size(os.path.getsize(input_file))
        after = human_readable.size(os.path.getsize(ffmpeg_params[-1]))

        print(BCOLORS.OKBLUE + before + BCOLORS.ENDC + " -> " + BCOLORS.OKGREEN + after + BCOLORS.ENDC)
        proc.wait()