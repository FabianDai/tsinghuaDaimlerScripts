#!/usr/bin/python
#   ----------------------
#   The Tsinghua-Daimler Cyclist Benchmark
#   ----------------------
#
#
#   License agreement
#-  ----------------
#
#   This dataset is made freely available for non-commercial purposes such as academic research, teaching, scientific publications, or personal experimentation. Permission is granted to use, copy, and distribute the data given that you agree:
#   1. That the dataset comes "AS IS", without express or implied warranty. Although every effort has been made to ensure accuracy, Daimler (or the website host) does not accept any responsibility for errors or omissions.
#   2. That you include a reference to the above publication in any published work that makes use of the dataset.
#   3. That if you have altered the content of the dataset or created derivative work, prominent notices are made so that any recipients know that they are not receiving the original data.
#   4. That you may not use or distribute the dataset or any derivative work for commercial purposes as, for example, licensing or selling the data, or using the data with a purpose to procure a commercial gain.
#   5. That this original license notice is retained with all copies or derivatives of the dataset.
#   6. That all rights not expressly granted to you are reserved by Daimler. 
#
#   Contact
#   -------
#
#   Fabian Flohr
#   mail: tdcb at fabian-flohr.de


import os
import sys
import argparse
import tarfile
import glob
import urllib
import hashlib    


downloadList = []

tdcb_labelData_train_url = ("http://www.gavrila.net/data/Daimler/iv16-li-flohr-gavrila-etal/tdcb_labelData_train.tar.gz", "7e17bca380056fd75e6e586ef0ed598a")
tdcb_labelData_test_url = ("http://www.gavrila.net/data/Daimler/iv16-li-flohr-gavrila-etal/tdcb_labelData_test.tar.gz", "cf63c6d0485fb7a0c8e7bd470f88cd66")
tdcb_labelData_valid_url = ("http://www.gavrila.net/data/Daimler/iv16-li-flohr-gavrila-etal/tdcb_labelData_valid.tar.gz", "2adb1ffc2f2b289108f1dfbae27fa2c4")
tdcb_labelData_nonvru_url = ("http://www.gavrila.net/data/Daimler/iv16-li-flohr-gavrila-etal/tdcb_labelData_NonVRU.tar.gz", "d589c5e27299721b69d63cd3face88d0")

tdcb_camera_train_url = ("http://www.gavrila.net/data/Daimler/iv16-li-flohr-gavrila-etal/tdcb_camera_train.tar.gz", "1925b6b9897b2865656cd00ba830c4c4")
tdcb_camera_test_url = ("http://www.gavrila.net/data/Daimler/iv16-li-flohr-gavrila-etal/tdcb_camera_test.tar.gz", "1434097ea7daeb22e64c15a54cd102c6")
tdcb_camera_valid_url = ("http://www.gavrila.net/data/Daimler/iv16-li-flohr-gavrila-etal/tdcb_camera_valid.tar.gz", "d0ae2e6d31b67880c0529ce97720e396")
tdcb_camera_nonvru_url = ("http://www.gavrila.net/data/Daimler/iv16-li-flohr-gavrila-etal/tdcb_camera_NonVRU.tar.gz", "ce67797cc6bb4878c621143b474769b9")


tdcb_leftImg8bit_train_url = ("http://www.gavrila.net/data/Daimler/iv16-li-flohr-gavrila-etal/tdcb_leftImg8bit_train.tar.gz", "03a0c18fd281ea770244d094936eedfe")
tdcb_leftImg8bit_test_url = ("http://www.gavrila.net/data/Daimler/iv16-li-flohr-gavrila-etal/tdcb_leftImg8bit_test.tar.gz", "82fc1f7983ab452bd0b1a5c874d04e89")
tdcb_leftImg8bit_valid_url = ("http://www.gavrila.net/data/Daimler/iv16-li-flohr-gavrila-etal/tdcb_leftImg8bit_valid.tar.gz", "f08c9fc63173b47fa0716e619e3b5a55")
tdcb_leftImg8bit_nonvru_url = ("http://www.gavrila.net/data/Daimler/iv16-li-flohr-gavrila-etal/tdcb_leftImg8bit_NonVRU.tar.gz", "64d76ee7c65f5ae7f8bb0b790e1984ec")

tdcb_disparity_train_url = ("http://www.gavrila.net/data/Daimler/iv16-li-flohr-gavrila-etal/tdcb_disparity_train.tar.gz", "2f4b2cd11d5066b6751a6b112d2a7405")
tdcb_disparity_test_url = ("http://www.gavrila.net/data/Daimler/iv16-li-flohr-gavrila-etal/tdcb_disparity_test.tar.gz", "d72375f453c83bce522edf78cfab9aa6")
tdcb_disparity_valid_url = ("http://www.gavrila.net/data/Daimler/iv16-li-flohr-gavrila-etal/tdcb_disparity_valid.tar.gz", "6366b94297a0efd2e1e1ab177a14f1fd")
tdcb_disparity_nonvru_url = ("http://www.gavrila.net/data/Daimler/iv16-li-flohr-gavrila-etal/tdcb_disparity_NonVRU.tar.gz", "b063cfd2670ca522d172b24e993c1e61")



tdcb_scripts_url = ("http://www.gavrila.net/data/Daimler/iv16-li-flohr-gavrila-etal/tdcb_scripts.tar.gz", "") #no checksum cause of possible git udpates



downloadList.append(tdcb_leftImg8bit_test_url)
downloadList.append(tdcb_leftImg8bit_train_url)
downloadList.append(tdcb_leftImg8bit_valid_url)
downloadList.append(tdcb_leftImg8bit_nonvru_url)

downloadList.append(tdcb_disparity_train_url)
downloadList.append(tdcb_disparity_test_url)
downloadList.append(tdcb_disparity_valid_url)
downloadList.append(tdcb_disparity_nonvru_url)

downloadList.append(tdcb_labelData_train_url)
downloadList.append(tdcb_labelData_test_url)
downloadList.append(tdcb_labelData_valid_url)
downloadList.append(tdcb_labelData_nonvru_url)

downloadList.append(tdcb_camera_train_url)
downloadList.append(tdcb_camera_test_url)
downloadList.append(tdcb_camera_valid_url)
downloadList.append(tdcb_camera_nonvru_url)

downloadList.append(tdcb_scripts_url)

#urlOpener = urllib.URLopener()



class myURLOpener(urllib.FancyURLopener):
    """Create sub-class in order to overide error 206.  This error means a
       partial file is being sent,
       which is ok in this case.  Do nothing with this error.
    """
    def http_error_206(self, url, fp, errcode, errmsg, headers, data=None):
        pass



# unpacks the Tswinghua Daimler Benchmark Dataset in the specified folder
def main(argv):
    parser = argparse.ArgumentParser(description='Automatic setup script for the Tsinghua-Daimler Cyclist Benchmark Dataset. Download of the necessary tar files and unpack them.')
    parser.add_argument('-o', '--datasetRootFolder', type=str, required=True,
                        help='Specifies where the dataset should be installed. If no separate tarFolder is given, tar files will be downloaded and/or suppposed to be in datasetRootFolder.')
    parser.add_argument('-t', '--tarFolder', type=str, required=False,
                        help='Specify if folder where tars should be downloaded is different to the datasetRootFolder')
    
    # parse options and get filelist
    opts = parser.parse_args(argv[1:])
    
    with open(os.path.dirname(os.path.realpath(__file__)) +"/LICENSE_public.txt",'r') as f:
    	file_contents = f.read()
    	print (file_contents)
    acceptLicenseAnswer = raw_input("Before using the Tsinghua-Daimler Bicyclist Dataset (TDBD) you are required to agree and accept the license terms. Type 'yes' if you have read and understand all of the terms: ")
    if not acceptLicenseAnswer == "yes":
	sys.exit(-1)

    datasetRootFolder = os.path.abspath(opts.datasetRootFolder)
    if not os.path.isdir(datasetRootFolder):
	    print("Output Folder does not exist..I will create it..")
	    os.makedirs(os.path.abspath(datasetRootFolder))

    if not opts.tarFolder:
	tarFolder = datasetRootFolder
    else:
	tarFolder = os.path.abspath(opts.tarFolder)

    if not os.path.isdir(tarFolder):
	    print("Input Folder does not exist..I will create it..")
	    os.makedirs(os.path.abspath(tarFolder))


    download(tarFolder)
    total = untar(tarFolder, datasetRootFolder)
    args = total, total > 1 and 's were' or ' was'
    print('Report: %s file%s untared.' % args)
    return 0

def dlProgress(count, blockSize, totalSize):
	percent = min(100, count*blockSize*100.0/totalSize)
	sys.stdout.write("\r ...%0.2f%% " % percent)
	sys.stdout.flush()





def download(tarFolder):
	print "\nChecksum verification and download if necessary ... (this can take a while)"
	for downloadFile in downloadList:
		# File to check   
		tarFileInBase = os.path.join(tarFolder, os.path.basename(downloadFile[0]))
		
		global downFile # global variable to be used in dlProgress
		downFile = downloadFile[0]

	

		if not os.path.exists(tarFileInBase) or not md5Check(downloadFile[1], tarFileInBase ):
			
			print "\nDownload file "+downFile

			try:
				downloadWithResume(tarFileInBase, downFile)
            			#urlOpener.retrieve(downFile, tarFileInBase, reporthook=dlProgress)
        		except:
				print "\nDownload of {} not possible. Make sure you're prox is correctly configured and you are not behind a firewall.".format(downFile)
				print "\nBye."
				sys.exit(1)
			
			
			# Open,close, read file and calculate MD5 on its contents
			md5Check(downloadFile[1], tarFileInBase )
    

def md5Check(originalChecksum, fileToCheck ):
		# Open,close, read file and calculate MD5 on its contents
		if not originalChecksum:
			print "No checksum available"
			return True
		print "\nMD5 checksumm check "+fileToCheck
		md5_returned = md5_for_file(fileToCheck)
		print md5_returned
		    

		# Finally compare original MD5 with freshly calculated
		if originalChecksum:
			if originalChecksum == md5_returned:
			    print "\nMD5 for {} verified.".format(fileToCheck)
			    return True
			else:
			    print "\nMD5 verification for {} failed!. Please delete tar.gz manually or/and execute setup.py again".format(fileToCheck)
			    sys.exit(1)
	 	


def downloadWithResume(dlFile,internetFile):
	loop = 1
	existSize = 0
	myUrlclass = myURLOpener()
	if os.path.exists(dlFile):
	    outputFile = open(dlFile,"ab")
	    existSize = os.path.getsize(dlFile)
	    #If the file exists, then only download the remainder
	    myUrlclass.addheader("Range","bytes=%s-" % (existSize))
	else:
	    outputFile = open(dlFile,"wb")

	webPage = myUrlclass.open(internetFile)

	#If the file exists, but we already have the whole thing, don't download again
	try:
		internetFileSize = int(webPage.headers['Content-Length'])
	except:
		print "I can't establish a connection to {}. Make sure your proxy setting are correct."
		sys.exit(-1)
	
	if internetFileSize == existSize:
	    loop = 0
	    print "File already downloaded"
	numBytes = 0
	while loop:
	    data = webPage.read(8192)
	    if not data:
		break
	    outputFile.write(data)
	    
	    numBytes = numBytes + len(data)
	    dlProgress(1, existSize + numBytes,internetFileSize) 
	webPage.close()
	outputFile.close()

	#for k,v in webPage.headers.items():
	#    print k, "=",v
	print "copied", numBytes, "bytes from", webPage.url


def md5_for_file(path, block_size=256*128):
    '''
    Block size directly depends on the block size of your filesystem
    to avoid performances issues
    Here I have blocks of 4096 octets
    '''
    md5 = hashlib.md5()
    fileSize = os.path.getsize(path)
    with open(path,'rb') as f: 
	count=1
        for chunk in iter(lambda: f.read(block_size), b''): 
             md5.update(chunk)
	     dlProgress(count, block_size, fileSize)
	     count=count+1
    return md5.hexdigest()


def untar(inputFolder, datasetRootFolder):
    print "Untar files ..."
    total = 0
    if os.path.isdir(inputFolder):
        try:
            dir_list = glob.glob(inputFolder + "/tdcb_*.tar.gz")
        except:
            pass
	
    for tarFile in dir_list:
        try:
            tarfile.open(tarFile).extractall(datasetRootFolder)
            print("Untared {} into {}".format(tarFile, datasetRootFolder))
        except:
            pass
        else:
            total += 1

    return total

if __name__ == '__main__':
    sys.exit((main(sys.argv)))
