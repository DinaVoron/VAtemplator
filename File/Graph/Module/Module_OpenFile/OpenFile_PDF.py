import PyPDF2
from Module.Console import Console

def open_pdf(path_to_file):
	pdf_file = open(path_to_file, "rb")
	if pdf_file:
		pdf = PyPDF2.PdfReader(pdf_file)
		if pdf:
			return pdf_file, pdf
		else:
			Console.LogError("OpenFile_PDF", "Не удалось прочитать файл.")
			return None, None
	else:
		Console.LogError("OpenFile_PDF", "Не удалось открыть файл.")
		return None, None

def close(pdf_file):
	Console.LogInfo("OpenFile_PDF", "Закрытие файла.")
	pdf_file.close()



def text(pdf_file, pdf):
	data = []
	for page in pdf.pages:
		data += [page.extract_text()]
	return data

# def info(pdf_file, pdf):
# 	pdf_info = pdf.metadata
# 	pages    = len(pdf.pages)

# 	Console.LogInfo("OpenFile_PDF", "Вывод информации о содержание файла.")
# 	Console.LogMessage(None, "Количество страниц в документе: %i" % pages)
# 	Console.LogMessage(None, f"Мета-описание: {pdf_info}\n")
# 	for i in range(pages):
# 		page = pdf.pages[i]

# 		Console.LogMessage(None, f"Страница: {i}\nМетаданные: {page}\nСодержание:")
# 		Console.LogMessage(None, page.extract_text())