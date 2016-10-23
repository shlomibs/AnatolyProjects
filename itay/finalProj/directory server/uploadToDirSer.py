from ftplib import FTP
import time, os

# file is FIN ! 

def uploadDir(path, ftp, sp): # sp = is subprocess?
	"""
	upload a directory to the ftp server
	"""
	files = os.listdir(path)
	os.chdir(path)
	filelist = [] #to store all files
	ftp.retrlines('LIST',filelist.append)    # append to list
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
		elif os.path.isdir(path + '/' + f):ft
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
		ftp = FTP('dirser.honor.es','u140460863','1346798255')
		ftp.cwd("dirSer")
		myPath = os.getcwd() 
		uploadDir(myPath, ftp, sp) # now call the recursive function
		if sp:
			return True
		print 'success'
		if sp
			return True
	except Exception as e:
		print "connection failed!!!\nerr: " + str(e)
		if sp:
			return False
	for i in range(3):
		write(".", sp)
		time.sleep(1)

def write(string, sp): #sp = subprocess
	if !sp: print string,

if __name__ == "__main__": # debugging or uploading manually
	if(len(sys.argv) > 1 && sys.argv[1] in ["subprocess","sp","SP"]):
		upload(True)
	else:
		upload(False)




