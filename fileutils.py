class FileUtils:

	@staticmethod
	def getExtension(fileName):
		return fileName[fileName.rfind('.'):]

	@staticmethod
	def getFileName(path):
		return path[path.rfind("/")+1:]

	@staticmethod
	def isFilePart(path):
                locked_extensions=['.filepart','.LOCK','.DAT']
		_filename = path[path.rfind("/")+1:]
		return _filename[_filename.rfind('.'):] in locked_extensions
