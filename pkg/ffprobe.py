import subprocess as sp
import json

def ffprobe(file: str) -> dict:
    proc = sp.Popen(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", file],
        stdout=sp.PIPE,
        stderr=sp.PIPE,
        universal_newlines=True)
    out, _ = proc.communicate()
    return json.loads(out)
