import magic
import os
import zipfile

from file_unzipper.exceptions import (
	UnzipperNotZipFile, UnzipperPasswordProtected, UnzipperFileTooLarge,
	UnzipperImageCompression, UnzipperFileSizeLimitFormat
)
from PIL import Image


class Unzipper():
	""" Unzipper instance
	
	An instance of the Unzipper class provides a way to validate and extract files from a zip file
	"""
	def __init__(self, allowed_file_extensions = [], image_compress = False, image_quality = 50, file_size_magic_number = 1024, delete_zip_file = False, allowed_file_size = None):
		""" Initialise an instance of Unzipper with the provided parameters
		
			* allowed_file_extensions -- A list of file extensions that can be extracted from the zip file e.g ['docx', 'jpeg']
			* image_compress -- A Boolean value that indicates whether unzipped files are to be compressed (ONLY works with images)
			* image_quality -- If image_compress, image_quality will be the compression factor; values from 1 - 100. Set to 50 by default
			* file_size_magic_number -- The magic number used to convert bytes to kilobytes and so on. Set too 1024 by default
			* delete_zip_file -- Once its contents have been extracted, the zip file is removed
			* allowed_file_size -- Maximum zip file size to be set in the format of '1 B', '1 KB', '1 MB' etc
		"""
		self.allowed_file_extensions = allowed_file_extensions
		self.image_compress = image_compress
		self.image_quality = int(image_quality)
		self.file_size_magic_number = int(file_size_magic_number)
		self.delete_zip_file = delete_zip_file
		self.allowed_file_size = allowed_file_size
		
		
	def unzip_file(self, path_to_zip_file, dir_to_extract_to, password = None):
		""" Unzip a zip file
		
			* path_to_zip_file -- The path to the zip file
			* dir_to_extract_to -- The directory to extract the contents of the zip file to
			* password -- If the zip file is password-protected, provide a password
		"""
		if self.zip_file_check(path_to_zip_file):
			pass
		else:
			raise UnzipperNotZipFile

		if self.password_protect_check(path_to_zip_file, password = None):
			pass
		else:
			raise UnzipperPasswordProtected

		zip_file_size = os.stat(path_to_zip_file).st_size

		if self.size_check(zip_file_size, self.allowed_file_size):
			pass
		else:
			raise UnzipperFileTooLarge

		files_check_result = self.file_list_check(path_to_zip_file, password = password)
		files_not_allowed = []
		
		if files_check_result[0]:
			pass
		else:
			files_not_allowed = files_check_result[1]

		zip_ref = zipfile.ZipFile(path_to_zip_file)
		
		file_list = zip_ref.infolist()

		for single in file_list:
			if single.filename in files_not_allowed:
				pass
			else:
				# Passing the ZipInfo object single as 'member'
				zip_ref.extract(single, path = dir_to_extract_to, pwd = str.encode(password))

				if self.image_compress:
					try:
						image_to_optimise = Image.open(dir_to_extract_to + "/" + single.filename)
						image_to_optimise.save(dir_to_extract_to + "/" + single.filename, optimize = True, quality = self.image_quality)
					except FileNotFoundError:
						raise UnzipperImageCompression

		if self.delete_zip_file:
			if os.path.isfile(path_to_zip_file):
				os.remove(path_to_zip_file)
	
	
	def zip_file_check(self, file):
		""" Checks if file mimetype is of type 'application/zip'
		
			* file -- The path to the zip file
		"""
		mime = magic.Magic(mime = True)
		mime_check = mime.from_file(file)
		
		if mime_check == "application/zip":
			return True
		else:
			return False
	
	
	def password_protect_check(self, file, password = None):
		""" Checks if zip file is password protected or if password provided is valid
		
			* file -- The path to the zip file
			* password -- The password for the zip file if file is password-protected
		"""
		zip_ref = zipfile.ZipFile(file)
		
		if password:
			""" zip_ref.setpassword requires that the password be byte-encoded
			"""
			encoded_pass = password.encode("utf-8")
		else:
			encoded_pass = None
			
		zip_ref.setpassword(encoded_pass)
	
		try:
			zip_ref.testzip()
			return True
		except RuntimeError:
			return False
		
	
	def size_check(self, file_size, size_limit = None):
		""" Checks if the zip file size is less than or equal to the size limit configured
		
			* file_size -- The zip file size provided in bytes
			* size_limit -- The limit set as '1 B', '1 KB' etc
		"""
		
		# File size suffixes
		suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

		def human_readable(no_of_bytes):
			""" Returns file size in a human-readable format in the format of '1 B', '1 KB' etc.
			
				* no_of_bytes -- The number of bytes to be converted
			"""
			i = 0

			while no_of_bytes >= self.file_size_magic_number and i < len(suffixes) - 1:
				# Dividing by 1024 and assigning the no_of_bytes variable to the result
				no_of_bytes /= self.file_size_magic_number
				i += 1
			formatted = ("%.2f" % no_of_bytes).rstrip("0").rstrip(".")
			return "%s %s" % (formatted, suffixes[i])

		if size_limit == None:
			return True
		else:
			try:
				limit_number, limit_suffix = size_limit.split(" ")
			except ValueError:
				raise UnzipperFileSizeLimitFormat
			file_number, file_suffix = human_readable(file_size).split(" ")

			# Checking position of file size suffix relative to position of limit suffix
			if suffixes.index(file_suffix) > suffixes.index(limit_suffix.upper()):
				return False
			elif suffixes.index(file_suffix) < suffixes.index(limit_suffix.upper()):
				return True
			elif suffixes.index(file_suffix) == suffixes.index(limit_suffix.upper()):
				if float(file_number) <= float(limit_number):
					return True
				else:
					return False
				
	
	def file_list_check(self, file, password = None):
		""" Checks if all the contents of the zip file match the file types in the allowed extensions list
		
			* file -- The path to the zip file
			* password -- The password for the zip file if file is password-protected
		"""
		zip_ref = zipfile.ZipFile(file)
		
		if password:
			""" zip_ref.setpassword requires that the password be byte-encoded
			"""
			encoded_pass = password.encode("utf-8")
		else:
			encoded_pass = None

		zip_ref.setpassword(encoded_pass)

		file_list = zip_ref.infolist()
		file_info = []

		if not self.allowed_file_extensions:
			return [True, []]
		else:
			for single in file_list:
				if single.filename.split(".")[1] in self.allowed_file_extensions:
					pass
				else:
					file_info.append(single.filename)

			if file_info:
				return [False, file_info]
			else:
				return [True, []]
