import pdfkit
from PyPDF2 import PdfMerger

# Configuration for pdfkit with the path to wkhtmltopdf
config = pdfkit.configuration(wkhtmltopdf=r'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')

# Step 1: Convert URLs to PDFs
url_english = "http://jy.zhhlzzs.com/EN/1672-9234/home.shtml"
url_non_roman = "http://jy.zhhlzzs.com/CN/1672-9234/home.shtml"

pdf_english_path = "toc_english.pdf"
pdf_non_roman_path = "toc_non_roman.pdf"

# Convert the English URL to PDF
pdfkit.from_url(url_english, pdf_english_path, configuration=config, options={'enable-local-file-access': ""})

# Convert the non-Roman URL to PDF
pdfkit.from_url(url_non_roman, pdf_non_roman_path, configuration=config, options={'enable-local-file-access': ""})

# Step 2: Merge PDFs
merged_pdf_path = "merged_toc.pdf"
merger = PdfMerger()

merger.append(pdf_english_path)
merger.append(pdf_non_roman_path)
merger.write(merged_pdf_path)
merger.close()

print(f"Merged PDF saved as {merged_pdf_path}")
