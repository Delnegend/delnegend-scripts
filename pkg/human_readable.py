def time(milisecond: int) -> str:
    seconds = milisecond / 1000
    if seconds >= 60 * 60:
        return f"{int(seconds/3600)}h{int(seconds%3600/60)}m{int(seconds%60)}s"
    elif seconds >= 60:
        return f"{int(seconds/60)}m{int(seconds%60)}s"
    else:
        return f"{seconds:.2f}s"


def size(byte: int) -> str:
    for unit in ["bytes", "KB", "MB", "GB"]:
        if byte < 1024.0:
            return f"{byte:.2f} {unit}"
        byte /= 1024.0
