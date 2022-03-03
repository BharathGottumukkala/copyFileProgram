from pathlib import Path
import time
import sys

# Dont use threading if the import fails
MODULE_PRESENT = True
try:
	import threading
except:
	print('Importing threading module failed')
	MODULE_PRESENT = False


# Chunk size for read/write = 4KB
CHUNK_SIZE = 4096

# Method to resolve symlinks and provide absolute path
def resolvePath(path):
	try:
		file = Path(path)
		return True, file.is_symlink(), file.resolve()
	except FileNotFoundError:
		return False, False, 'File Not Found'
	except RuntimeError:
		return False, False, 'Unexpected Error occured while parsing path'


# Method to read file in Chunks
def readFile(file, chunkSize=CHUNK_SIZE):
	while True:
		data = file.read(chunkSize)
		if not data:
			break

		yield data

# Method to check if the given path is a directory
def isDirectory(path):
	return Path.exists(path) and path.is_dir()

# Method used to copy source filename
def getFileNameFromPath(path: str):
	return path.split('/')[-1]

# Helper to call write from a thread
def callWrite(fileObject, data):
	fileObject.write(data)

def writeToFile(srcFile, destFile, use_threading=False):
	threads = [] # Store the threads, lengthshould not exceed 2 as we wait for the first thread to finish
	dest = destFile.open('wb') 
	with srcFile.open('rb') as source:
		for data in readFile(source): # Read file in chunks of CHUNK_SIZE
			if use_threading and MODULE_PRESENT:
				# Using threading to optimize on read while the thread finishes a slow write. 
				if(len(threads)):
					threads[-1].join()
					# delete the threads that have completed execution
					del threads[-1]

				# Start a new thread to write the data that is read from src file
				threads.append(threading.Thread(target=callWrite, args=(dest, data)))
				threads[-1].start()
			else:
				# Use syncronous write when threading module is missing or when threading overhead is too large when compared to writing speeds
				callWrite(dest, data)

def copyFiles(srcPath: str, destPath: str = None):

	# Check if destPath is provided. If it is not, return Error
	if srcPath is None or destPath is None:
		raise Exception('Please provide a source File and a destination folder/file')
	# Convert srcPath and destPath to absolute paths and remove any symlinks
	srcExists, srcSymLink, srcFile = resolvePath(srcPath)
	if srcExists:
		srcFileSize = srcFile.stat().st_size
	destExists, destSymLink, destFile = resolvePath(destPath)

	# If destination is a file name and that file doesnot exist - showing error
	if(not srcExists or not destExists):
		errorMsg = 'Both source and destination paths provided do not exist' if not srcExists and not destExists else 'The provided destiation path doesnot exist' if not destExists else 'The provided source path doesnot exist'
		raise Exception(errorMsg)


	# Check if destPath is a directory
	if isDirectory(destFile):
		# destination is a directory, copy source file name
		destFile = Path(str(destFile) + getFileNameFromPath(str(srcFile)) if str(destFile)[-1] == '/' else str(destFile) + '/' + getFileNameFromPath(str(srcFile)))

	if destSymLink:
		startTime = time.time()
		writeToFile(srcFile, destFile, use_threading=True)
		timeElapsed= time.time() - startTime
	else:
		# If copying within the sae harddisk, threading overhead is considerable. so avoinding creating multiple threads
		# Canbe optimized given a live instance with multiple network shared folders
		startTime = time.time()
		writeToFile(srcFile, destFile)
		timeElapsed= time.time() - startTime

	
	print('Average data transfer rate: ' + str(round((srcFileSize/1024) / timeElapsed, 2)) + ' KB/s' )

if __name__ == '__main__':
	totalArgs = len(sys.argv)

	if totalArgs != 3:
		print('-- Help Usage')
		print('python3 copyFiles.py <src_file> <dest_Folder>')
		exit()

	copyFiles(sys.argv[1], sys.argv[2])

