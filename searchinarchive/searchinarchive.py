

##################################
# Author: Charles 2013-02-10
# Simple Call with plain text: C:\Python33\python.exe F:\PythonWorkspace\searchinarchive.py fvt E:\document\DSW12.4\SDMA\sdmaEAR.ear
# Simple Call with Regular Expression: C:\Python33\python.exe F:\PythonWorkspace\searchinarchive.py .*fvt.* E:\document\DSW12.4\SDMA\sdmaEAR.ear
# This tool is used to search text in a archived EAR. 
# User just need to input search text and the full path of the EAR that need be searched in.
# It will use 7-Zip to extract the EAR, and search the text in all the plain text file types and ignore the binary files
##################################


import os
import re
import glob
import datetime
import time
import sys
import shutil

class SearchInArchive:
	# binary file types that will be skipped in the search scope
	excludeFileType = ['.class', '.war', '.jar', '.gif', '.png', '.jpg', '.pdf', '.rtf']
	
	# store the search results
	searchResult = []
	
	def __init__(self, searchText, sourceArchiveFile):
		# full path of the source EAR
		self.sourceArchiveFile = sourceArchiveFile
		# search text, it can be Regular Expression or plain text
		self.searchText = searchText
		# the top folder of the extracted EAR
		self.extractFolder = self.getDirByArchiveFileRealPath(self.sourceArchiveFile)
	
	def splitFileWithFullPath(self, archiveWithFullPath):
		dir, fileNameWithExt = os.path.split(archiveWithFullPath)
		fileName, ext = os.path.splitext(fileNameWithExt)
		return (dir, fileNameWithExt, fileName, ext)
	
	def extractWith7Zip(self, archiveFileRealPath):
		outputDir = self.getDirByArchiveFileRealPath(archiveFileRealPath)
		
		# use 7-zip to extract the archive file, so need add the path of 7-zip into Path environment variables
		# x option will extract the all the files in the original folder
		# -aou will rename the files with same name
		# -y will automatically override the alert with 'Yes'
		os.system('cmd /c 7z x -t* \"' + archiveFileRealPath + '\" -y -aou -o' + outputDir)
		
		return outputDir
	
	
	# this can be extended to filter which jars need be extracted
	def isNeedExtract(self, fileNameWithExt):
		return (fileNameWithExt.count('.') == 1 and '-' not in fileNameWithExt)
		
	def extractArchive(self):
		earDir = self.extractWith7Zip(self.sourceArchiveFile)
		# it will process the war and jar archives in the first level folder of the EAR
		for warName in glob.glob(earDir + '\\*.war'):
			warDir = self.extractWith7Zip(os.path.join(earDir + '\\', warName))
			webInfoLibDir = warDir + '\\WEB-INF\\lib'
			for jarInWarName in glob.glob(webInfoLibDir + '\\*.jar'):
				jarDir, jarName = os.path.split(jarInWarName)
				if self.isNeedExtract(jarName):
					self.extractWith7Zip(jarInWarName)
			
		for jarInEarName in glob.glob(earDir + '\\*.jar'):
			self.extractWith7Zip(os.path.join(earDir + '\\', jarInEarName))	
	
	# get the dir from archiveFileReal path, for example, will return 'E:\document\DSW12.4\SDMA\sdmaEAR' if the EAR is 'E:\document\DSW12.4\SDMA\sdmaEAR.ear'
	def getDirByArchiveFileRealPath(self, archiveFileRealPath):
		return archiveFileRealPath[ : archiveFileRealPath.rindex('.')]
	
	# search the text in file by line, support Regular Expression
	def searchInFileByLine(self, file, searchText):
		# open the plain text file with UTF-8 encoding first, if the file is not in UTF-8, open the file in default encoding
		try:
			a_file = open(file, 'r', encoding='utf-8')
			allLines = a_file.readlines()
			lineNum = 0
			for line in allLines:
				lineNum += 1
				if re.search(searchText, line):
					self.searchResult.append('Find text in file: ' + file + ', line number: ' + str(lineNum) + ', line: ' + line.strip())
		except:
			a_file.close()
			try:
				# open the file in default encoding
				b_file = open(file, 'r')
				allLines_b = b_file.readlines()
				lineNum_b = 0
				for line_b in allLines_b:
					lineNum_b += 1
					if re.search(searchText, line_b):
						self.searchResult.append('Find text in file: ' + file + ', line number: ' + str(lineNum_b) + ', line: ' + line_b.strip())
			except:
				# do nothing
				print('Ignore binary file ' + file)
			finally:
				b_file.close()
		else:	
			a_file.close()
		
	# search the text in all the files excludes the binary files
	def searchInFiles(self, directory):	
		for fileOrDir in glob.glob(directory +'\\*'):
			if os.path.isfile(fileOrDir):
				dir, fileNameWithExt, fileName, ext = self.splitFileWithFullPath(fileOrDir)
				# exclude the file types in self.excludeFileType list
				if ext.lower() not in self.excludeFileType:
					self.searchInFileByLine(fileOrDir, self.searchText)
			elif os.path.isdir(fileOrDir):
				self.searchInFiles(fileOrDir)
	
	def printResult(self):
		dir, fileName = os.path.split(self.sourceArchiveFile)
		resultFile = dir + '\\' + fileName + '-result.txt'
		with open(resultFile, 'w', encoding='utf-8') as result_file:
			if len(self.searchResult):
				result_file.write('\nFound ' + str(len(self.searchResult)) + ' result contain the text: ' + self.searchText + '\n')
				for result in self.searchResult:
					result_file.write(result + '\n')
			else:
				result_file.write('Not found text \"' + self.searchText + '\" in archive file ' + self.sourceArchiveFile)
		
		print('Search successfully! Please find the result in ' + resultFile)
		os.system('cmd /c notepad ' + resultFile)
		
	
	# check if need re-extract the EAR, if the EAR is just extract in 1 hour, no need to extract again
	# this can enable searching multiple times in the EAR and just need extract once
	def needReExtract(self):
		# if not extract before, extract it
		if not os.path.exists(self.extractFolder):
			return True
		
		# check the top level extracted folder mod time	
		folderTimeInfo = time.localtime(os.stat(self.extractFolder).st_mtime)
		folderModTime = datetime.datetime(folderTimeInfo[0], folderTimeInfo[1], folderTimeInfo[2], folderTimeInfo[3], folderTimeInfo[4], folderTimeInfo[5])
		nowTime = datetime.datetime.now() 
		timeDelta = (nowTime - folderModTime).seconds / 60 / 60
		# if extracted than 1 hour, delete the extract folder and re-extract
		if timeDelta > 1:
			self.deleteExtractedFile()
			return True
		else:
			return False
	
	# delete the extracted files
	def deleteExtractedFile(self):
		shutil.rmtree(self.extractFolder)
		print('Deleted old files: ' + self.extractFolder)
		
	def doSearch(self):
		try:
			if self.needReExtract():
				self.extractArchive()
				
			self.searchInFiles(self.extractFolder)
			self.printResult()
		except(RuntimeError) as e:
			print(e)
		
if __name__ == '__main__':
	# Simple Call with plain text: C:\Python33\python.exe F:\PythonWorkspace\searchinarchive.py fvt E:\document\DSW12.4\SDMA\sdmaEAR.ear
	# Simple Call with Regular Expression: C:\Python33\python.exe F:\PythonWorkspace\searchinarchive.py .*fvt.* E:\document\DSW12.4\SDMA\sdmaEAR.ear
	obj = SearchInArchive(sys.argv[1], sys.argv[2])
	obj.doSearch()
	
