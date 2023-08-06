import subprocess as sp


def dimension(path: str):
    try:
        result = sp.run(
            f'ffprobe -v error -select_streams v -show_entries stream=width,height -of csv=p=0:s=x "{path}"',
            shell=True,
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            check=True,
        )
        w, h = result.stdout.decode("utf-8").split("x")
        return (int(w), int(h))
    except:
        return (0, 0)
