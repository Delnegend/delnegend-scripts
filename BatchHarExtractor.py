import glob
import os
import re
for elem in glob.glob("*.har"):
  folderPath = re.sub(r'\.har',"",elem)
  os.system('har-extractor.cmd "'+elem+'" --output "'+folderPath+'"')