import os
import sys
import glob
for elem in glob.glob("*.mkv"):
  # filename = os.path.splitext("base")[0]
  # userParams = sys.argv
  # userParams.pop(0)
  # fileName = userParams[0].replace('.\\','')
  fileName = '"'+elem+'"'
  fileName_ = elem
  folderName = '"'+os.path.splitext(fileName_)[0]+'"'
  folderName_ = os.path.splitext(fileName_)[0]
  # print(folderName)
  os.system('mkdir ' + folderName)
  os.system('move ' + fileName + " " + folderName)
  os.system('copy batch_mkv_to_hls_extension.bat ' + folderName)
  os.chdir(folderName_)
  os.system('batch_mkv_to_hls_extension.bat ' + fileName)
  os.rename(r'p.m3u8',r'index.m3u8')
  os.chdir('../')
