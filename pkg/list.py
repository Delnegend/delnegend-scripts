import os


def file(path: str, ext: list, recursive=True, get_full_path=False):
    full_path = os.path.abspath(path) if not os.path.isabs(path) else path
    rel_path = os.path.relpath(path, os.getcwd())
    files = []
    for f in os.listdir(path):
        if os.path.isfile(os.path.join(path, f)):
            if len(ext) > 0 and os.path.splitext(f)[1].lower() in ext:
                files.append(os.path.join(full_path, f) if get_full_path else os.path.join(rel_path, f))
            elif len(ext) == 0:
                files.append(os.path.join(full_path, f) if get_full_path else os.path.join(rel_path, f))
        else:
            if recursive:
                files += file(os.path.join(path, f), ext, recursive, get_full_path)
    return files


def folder(path: str, recursive=True):
    # list folders recursively in path
    folders = []
    for f in os.listdir(path):
        if os.path.isdir(os.path.join(path, f)):
            folders.append(os.path.join(path, f))
            if recursive:
                folders += folder(os.path.join(path, f), recursive)
    return folders
