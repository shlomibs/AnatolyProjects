#!/usr/bin/python
from ftplib import FTP
import time, os, sys

# file is FIN ! 

def uploadDir(path, ftp, sp): # sp = is subprocess?
	"""
	upload a directory to the ftp server
	"""
	files = os.listdir(path)
	os.chdir(path)
	filelist = [] #to store all files
	#ftp.retrlines('LIST',filelist.append)    # append to list
	ftp.dir(filelist.append)
	filelist = [i[55:] for i in filelist[2:]] # by format
	for f in files:
		if f == "upload to dirSer.py":
			write(f + " skipped\n", sp)
			continue
		if os.path.isfile(path + '/' + f):
			write("starting to upload file: " + str(f), sp)
			fh = open(f, 'rb')
			ftp.storbinary('STOR %s' % f, fh)
			fh.close()
			write("               uploaded\n", sp)
		elif os.path.isdir(path + '/' + f):
			exist = False
			for file1 in filelist:
				if f in file1:
					exist = True
			if not exist:
				ftp.mkd(f)
			ftp.cwd(f)
			write("\nstarting to upload dir: " + str(f) + "\n", sp)
			uploadDir(path + '/' + f)
			write("dir uploaded\n\n", sp)
	ftp.cwd('..')
	os.chdir('..')

# sp = false for debugging or uploading manually
def upload(sp): # sp = is subprocess?
	try:
		#ftp = FTP('dirser.honor.es','u140460863','1346798255')
		#ftp = FTP('dirser.honor.es','nurealnetwork','1346798255')
		ftp = FTP('dirser.atwebpages.com','2242349','Iitay1346')
		ftp.cwd("dirser.atwebpages.com")
		ftp.cwd("dirSer")
		myPath = os.getcwd() + "/upload"
		# upload the ../upload folder to dirSer # upload full dir for future updates
		uploadDir(myPath, ftp, sp) # now call the recursive function
		if sp:
			return True
		print 'success'
	except Exception as e:
		print "connection failed!!!\nerr: " + str(e)
		if sp:
			return False
	if sp:
		return True;
	for i in range(3):
		write(".", sp)
		time.sleep(1)
	return True

def write(string, sp): #sp = subprocess
	if not sp: print string,

if __name__ == "__main__": # debugging or uploading manually
	if(len(sys.argv) > 1 and sys.argv[1] in ["subprocess","sp","SP"]):
		upload(True)
	else:
		upload(False)




