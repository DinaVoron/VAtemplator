import re
import Module.Module_OpenFile.OpenFile_PDF as OpenFile_PDF
import Module.Console

class File:
	def __init__(self, type_file, path_to_file, file, file_read):
		self.type_file    = type_file
		self.path_to_file = path_to_file
		self.file         = file
		self.file_read    = file_read

		self.f_text = None

	def empty(self):
		if self.type_file:
			if self.path_to_file:
				if self.file:
					if self.file_read:
						return False
		return True



	def text(self, fl = False, border = [None, None], replacement = []):
		if self.empty():
			Console.LogWarn("OpenFile", "Файл пуст.")
		else:
			text = ""
			if self.type_file == "PDF":
				if self.f_text:
					text = self.f_text[border[0] : border[1]]
				else:
					self.f_text = OpenFile_PDF.text(self.file, self.file_read)
					text = self.f_text[border[0] : border[1]]

			if fl:
				pages, text = text, ""
				for page in pages:
					text += page
				for replace in replacement:
					text = re.sub(replace[0], replace[1], text, flags=re.DOTALL)
				return text
			else:
				for replace in replacement:
					text = re.sub(replace[0], replace[1], text, flags=re.DOTALL)
				return text

				 


def open_pdf(path_to_file):
	pdf_file, pdf = OpenFile_PDF.open_pdf(path_to_file)

	if pdf_file and pdf:
		return File("PDF", path_to_file, pdf_file, pdf)
	return File(None, None, None, None)

def close(file):
	if file.empty():
		Console.LogWarn("OpenFile", "Файл пуст.")
	else:
		if file.type_file == "PDF":
			OpenFile_PDF.close(file.file)
			

# 		if file.
# 			

# # IS

# #

# def info(file):
# 	if file.empty():
# 		Console.LogWarn("OpenFile", "Файл пуст.")
# 	else:
# 		if file.type_file == "PDF":
# 			Module._OpenFile_PDF.info(file.file, file.file_read)
# 			return