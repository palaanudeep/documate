import os
import io
from PyPDF2 import PdfReader
from pdfminer.high_level import extract_text
from docx import Document
from werkzeug.utils import secure_filename

def extract_text_from_file(file):
    filename = secure_filename(file.filename)
    file_extension = os.path.splitext(filename)[1]

    if file_extension == '.txt':
        print('TEXT FILE')
        text = file.stream.read().decode('utf-8')
    elif file_extension == '.docx':
        print('DOCX FILE')
        doc = Document(io.BytesIO(file.stream.read()))
        text = ' '.join([paragraph.text for paragraph in doc.paragraphs])
    elif file_extension == '.pdf':
        print('PDF FILE')
        # pdf = PdfReader(io.BytesIO(file.stream.read()))
        # text = ' '.join([page.extract_text() for page in pdf.pages])
        text = extract_text(io.BytesIO(file.stream.read()))
    else:
        text = ''

    return text