import glob, os, shutil, pathlib

def filesize(item):
  return os.stat(item).st_size

tempPathName = "newFilesBigger"

pathlib.Path(tempPathName).mkdir(parents=True, exist_ok=True)

oldFormat = input("Old file format: ")
newFormat = input("New file format: ")

allNewFiles = glob.glob("*."+newFormat)
for newFile in allNewFiles:
  oldFile = newFile.replace("."+newFormat,"."+oldFormat)
  if (filesize(newFile) >= filesize(oldFile)):
    shutil.move(newFile, tempPathName)
    shutil.move(oldFile, tempPathName)