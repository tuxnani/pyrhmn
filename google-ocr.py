import glob
import os


files = []
for filename in glob.glob('*.jpg'):
        files.append(filename)

for image in sorted(files):
	print "uploading " + image
	command = "gdput.py -t ocr  " + image + " > result.log"
	print "running " + command
	os.system(command)
	resultfile = open("result.log","r").readlines()
	for line in resultfile:
		if "id:" in line:
			fileid = line.split(":")[1].strip()
			filename = image.split(".")[0] + ".docx"
			get_command = "gdget.py -f docx -s " + filename + " " + fileid
			print "running "+ get_command
			os.system(get_command)
print "Done"
