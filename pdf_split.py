from pyPdf import PdfFileWriter, PdfFileReader

inputpdf = PdfFileReader(file("output.pdf", "rb"))

for i in xrange(inputpdf.numPages):
 output = PdfFileWriter()
 output.addPage(inputpdf.getPage(i))
 outputStream = file("document-page%s.pdf" % i, "wb")
 output.write(outputStream)
 outputStream.close()
