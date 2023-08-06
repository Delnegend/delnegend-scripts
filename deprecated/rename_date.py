import os
import re


class BCOLORS:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def norm(path):
    return os.path.normpath(path).replace("\\", "/")


def listFiles(path, recursive=False):
    if recursive:
        return [norm(os.path.join(norm(dp), norm(f))) for dp, dn, filenames in os.walk(path) for f in filenames]
    else:
        return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]


def main():
    for name in listFiles(".", recursive=True):
        res = re.search(r"\[(\d{4}\.\d{2})\]", name)
        date_ = res.group() if res else ""
        date = date_.replace("[", "").replace("]", "")
        new_name = os.path.join(
            os.path.dirname(name),
            date + (" " if date else "") + os.path.basename(name.replace(date_, "")),
        )
        new_name = new_name.replace(" .zip", ".zip").replace(" .7z", ".7z").replace("\\", "/")
        if name.replace("\\", "/") != new_name:
            print(BCOLORS.OKGREEN + name + BCOLORS.ENDC + " -> " + BCOLORS.OKBLUE + new_name + BCOLORS.ENDC)
            os.rename(name, new_name)


if __name__ == "__main__":
    main()
