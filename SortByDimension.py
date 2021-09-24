# Requirement(s): Pillow
from PIL import Image
from os import listdir, system
from os.path import isfile, join
from pathlib import Path
from shutil import move

Path("./Potrait/").mkdir(parents=True, exist_ok=True)
Path("./Square/").mkdir(parents=True, exist_ok=True)
Path("./Landscape/").mkdir(parents=True, exist_ok=True)
filelist = [f for f in listdir("./") if isfile(join("./", f))]
for file in filelist:
  try:
    img = Image.open(file)
    width, height = img.size
    img.close()
    if width < height:
      move(file, './Potrait/'+file)
    elif width == height:
      move(file, './Square/')
    elif width > height:
      move(file, './Landscape/')
  except:
    print("Not An Image")