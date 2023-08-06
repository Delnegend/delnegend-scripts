import json
import subprocess as sp


def ffprobe(file: str, ffprobe_binary: str = "ffprobe") -> dict:
    proc = sp.Popen(
        [
            ffprobe_binary,
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            file,
        ],
        stdout=sp.PIPE,
        stderr=sp.PIPE,
        universal_newlines=True,
    )
    out, _ = proc.communicate()
    return json.loads(out)
