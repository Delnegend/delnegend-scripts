from os import chdir, listdir
from os.path import isfile, join
from os import system
from shutil import move
for item in [f for f in listdir(".") if not isfile(join(".", f))]:
    chdir(item)
    system("7z.exe a -bt -x\"!*.ini\" -m0=Deflate64 -r \"" + item + ".zip\" *.*\"")
    move(item + ".zip", "..")
    chdir("..")