import PyPDF2
import pdfminer.high_level
import pdfminer.layout
from io import StringIO, BytesIO
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTText
from pdfminer.pdfparser import PDFSyntaxError

def extract_text(filename):
    with open(filename, 'rb') as f:
        try:
            reader = PyPDF2.PdfReader(f)
            if reader.is_encrypted:
                reader.decrypt('')
        except PyPDF2._utils.PdfStreamError:
            return ''
        outfp = StringIO()
        laparams = LAParams()
        pdfminer.high_level.extract_text_to_fp(f, outfp, laparams=laparams)
        return outfp.getvalue()

def get_text_and_style(text):
    text_and_style = []
    for page in PDFPage.get_pages(BytesIO(text.encode('utf-8'))):
        for obj in page.resources.objects:
            if isinstance(obj, pdfminer.pdfdocument.PDFStream) and 'Font' in obj:
                font_dict = obj['Font'].resolve()
                for font in font_dict.values():
                    if hasattr(font, 'fontname') and hasattr(font, 'fontsize'):
                        fontname = font.fontname
                        fontsize = font.fontsize
                        break
        device = PDFPageAggregator(rsrcmgr, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        interpreter.process_page(page)
        layout = device.get_result()
        for obj in layout:
            if isinstance(obj, LTText):
                text_and_style.append((obj.get_text(), fontsize))
    return text_and_style


# Example usage:
filename = '/Users/suhaniagarwal/Desktop/hackmol/suhaniAgarwal.pdf'
text = extract_text(filename)
print(text)
text_and_style = get_text_and_style(text)
for item in text_and_style:
    print(f'Text: {item[0]} \nSize: {item[1]} \nFont: {item[2]}')

