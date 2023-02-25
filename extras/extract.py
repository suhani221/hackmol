import sqlite3
from PyPDF2 import PdfReader

conn = sqlite3.connect('apple.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS pages (
    url TEXT,
    content TEXT
)
''')

//extract font size too?

with open('/Users/suhaniagarwal/Desktop/hackmol/W03_L2_Query_languages_1.pdf', 'rb') as file:
    pdf = PdfReader(file)
    for i in range(len(pdf.pages)):
        page = pdf.pages[i]
        text = page.extract_text()
        cursor.execute('INSERT INTO pages (url, content) VALUES (?, ?)', (f'page{i + 1}', text))

conn.commit()
conn.close()

