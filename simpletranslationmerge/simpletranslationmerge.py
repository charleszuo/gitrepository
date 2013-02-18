
##################################
# Author: Charles 2013-02-01
# Simple Call: C:\Python33\python.exe F:\translatedproperties E:\workspace\sdmaPassport\JavaSource\appl\i18n sdma
# This tool is used to simplify the translation merge work. 
# User just need to input the translated file folder, the target properties foloder, and the properties file name without locale.
# It will automatically run native2acsii command to encode translated file, then map the translated content to target properties and merge it.
##################################

import os
import re
import glob
import sys

class SimpleTranslationMerge:
	translated_file_content = {}
	targetFileNames = []
	# key is locale in translated properties file, value is the locale in target properties file
	# for example translated file for Latam spanish is sdma_es_LA.properties, 
	# the real properties for Latam spanish is sdma_es_MX.properties, so the mapping is 'es_LA': 'es_MX'
	source_target_locale_mapping = {'en_US': 'en_US', 'de_DE': 'de_DE', 'fr_FR': 'fr_FR', 'it_IT': 'it_IT', \
								'es_ES': 'es_ES', 'nl_NL': 'nl_NL', 'ja_JP': 'ja_JP', 'es_LA': 'es_MX', 'fr_CA': 'fr_CA', \
								 'pt_BR': 'pt_BR', 'zh_CN': 'zh_CN', 'bg_BG': 'bg_BG', 'cs_CZ': 'cs_CZ', 'da_DK': 'da', \
								'fi_FI': 'fi_FI', 'hr_HR': 'hr_HR', 'hu_HU': 'hu_HU', 'ko_KO': 'ko', 'no_NO': 'no', \
								'ru_RU': 'ru', 'sk_SK': 'sk_SK', 'sl_SI': 'sl_SI', 'sv_SE': 'sv_SE', 'tr_TR': 'tr_TR', 'zh_TW': 'zh_TW', \
								'lt_LT': 'lt_LT', 'id_ID': 'id_ID', 'el_GR': 'el_GR', 'pl_PL': 'pl_PL'}
								
	def __init__(self, sourcePath, targetPath, targetFile):
		self.sourcePath = sourcePath
		self.targetPath = targetPath
		self.targetFile = targetFile
		os.chdir(self.sourcePath)
		# folder to put encoded files
		self.encodedFileFolder = 'encodedfiles'
		self.validateFileFolder = 'validate'
		self.validateFile = 'native_utf8.properties'
		
	def encodeProperties(self):
		if(not os.path.exists(self.encodedFileFolder)):
			os.system('mkdir '+ self.encodedFileFolder)
		native2ascii = os.environ.get("JAVA_HOME") + '\\bin\\native2ascii'
		
		for file in glob.glob('*.properties'):
			os.system('cmd /c \"' + native2ascii + '\" -encoding utf-8 ' + file + ' ' + self.encodedFileFolder + '\\'+ file)
			print('Successfully encode properties file: ' + file)
			
	def loadEncodedPropertiesContent(self):
		os.chdir(self.encodedFileFolder)
		for encodedFileName in glob.glob('*.properties'):
			sourceLocaleCode = self.getLocaleCode(encodedFileName)
			targetLocaleCode = self.source_target_locale_mapping[sourceLocaleCode]
			targetFileName = self.targetFile + '_' + targetLocaleCode + '.properties'
			self.targetFileNames.append(targetFileName)
			with open(encodedFileName, encoding='utf-8') as encoded_file:
				firstLine = encoded_file.readline()
				# sometimes the UTF-8 file encoded, it will append a \ufeff BOM to the encoded file, remove it
				if firstLine.lower().startswith('\ufeff') or firstLine.lower().startswith('\ufffe'):
					firstLine = firstLine[1:]
				allLines = list(encoded_file)
				allLines.insert(0, firstLine)
				# remove the comment lines
				contentDict = dict([line.strip().split('=', 1) for line in allLines if not line.strip().startswith('#') and '=' in line])
				self.translated_file_content[targetFileName] = contentDict
		
	def getLocaleCode(self, file):
		fileName, fileExt = os.path.splitext(file)
		# ord(fileName[-1]) get the ascii of last char of the fileName, > 90 means it is lower and the locale length is 2
		# < 90 means the locale lenght is 5
		if ord(fileName[-1]) > 90:
			return fileName[-2 : ]
		else:
			return fileName[-5 : ]
		
	def mergeTranslation(self):		
		for targetFileName in self.targetFileNames:
			targetFileRealPath = self.getFileRealPath(self.targetPath, targetFileName) 
			try:
				temp_file = open(targetFileRealPath)
				temp_content = temp_file.read()
				temp_content += '\n'
				temp_file.close()
			
				with open(targetFileRealPath, 'w') as write_file:
					translations = self.translated_file_content[targetFileName]
					for key in translations.keys():
						if re.search(key + '=.*\n', temp_content):
							# if the key already exists in the target properties, replace it
							merged_content = re.sub(key + '=.*\n', key + '=' + translations[key] + '\n', temp_content)
							temp_content = merged_content
						else:
							# if the key not exists in the target properties, append it at the end of the properties file
							temp_content += key + '=' + translations[key] + '\n'
					if temp_content.endswith('\n\n'):
						temp_content = temp_content[ : -1]
					write_file.write(temp_content)
			except:
				print('File not found: ' + targetFileRealPath)
				
			print('Successfully merged translations to properties file ' + targetFileRealPath)
	
	def getFileRealPath(self, path, fileName):
		if '/' in path and path.endswith('/'):
			return os.path.join(path, fileName)
		elif '/' in path and not path.endswith('/'):
			return os.path.join(path + '/', fileName)
		elif '\\' in path and path.endswith('\\'):
			return os.path.join(path, fileName)
		elif '\\' in path and not path.endswith('\\'):
			return os.path.join(path + '\\', fileName)
		else:
			return ''
	
	def validateTranslatedContent(self):
		os.chdir('..')
		if(not os.path.exists(self.validateFileFolder)):
			os.system('mkdir '+ self.validateFileFolder)
		os.chdir(self.validateFileFolder)
		
		with open(self.validateFile, 'w', encoding = 'utf-8') as validate_file:
			fileNames = self.translated_file_content.keys()
			for fileName in fileNames:
				validate_file.write('Text in native language for ' + fileName + ' is below: \n')
				translations = self.translated_file_content[fileName]
				for key in translations.keys():
					content = key + '=' + translations[key]
					# change Unicode String to native character
					nativeContent = eval('u' + '\"' + content + '\"')
					validate_file.write(nativeContent + '\n')
				validate_file.write('-----------------------------------------------------\n\n\n')
			
			print('validate file generated at ' + os.getcwd() + '\\' + self.validateFileFolder + '\\' + self.validateFile)
			
	def doTranslationMerge(self):
		try:
			self.encodeProperties()
			self.loadEncodedPropertiesContent()
			self.mergeTranslation()	
			self.validateTranslatedContent()
		except:
			print('Unknow exception thrown, please check your properties files')
	
if __name__ == '__main__':
	argsLen = len(sys.argv)
	if(argsLen != 4):
		print('Please input correct parameters')
	else:
		# sys.argv[1]: folder contains translated source properties
		# sys.argv[2]: folder contains properties file that need merge translation
		# sys.argv[3]: target properties file name without locale, if target file is sdma_en_US.properties, the parameter is sdma
		# Sample call: C:\Python33\python.exe F:\translatedproperties E:\workspace\sdmaPassport\JavaSource\appl\i18n sdma
		obj = SimpleTranslationMerge(sys.argv[1], sys.argv[2], sys.argv[3]) 
		obj.doTranslationMerge()
