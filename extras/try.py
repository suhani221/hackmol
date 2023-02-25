from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar
import sqlite3

# Connect to the database
conn = sqlite3.connect('orange.db')
c = conn.cursor()

# Create the table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS orange
             (Sentence text, Font_Size real, Page_Number integer)''')

for page_number, page_layout in enumerate(extract_pages("W02_L3_Data_formats.pdf"), start=1):
    for element in page_layout:
        if isinstance(element, LTTextContainer):
            sentence = ""
            font_size = None
            for text_line in element:
                for character in text_line:
                    if isinstance(character, LTChar):
                        if font_size is None:
                            font_size = round(character.size)
                        if character.get_text():
                            sentence += character.get_text()
                        else:
                            if sentence:
                                # Insert the data into the database
                                c.execute("INSERT INTO orange (Sentence, Font_Size, Page_Number) VALUES (?, ?, ?)", (' '.join(sentence.split()), font_size, page_number))
                                conn.commit()
                            sentence = ""
                            font_size = None
            if sentence:
                # Insert the data into the database
                c.execute("INSERT INTO orange (Sentence, Font_Size, Page_Number) VALUES (?, ?, ?)", 
                          ('hi '.join(sentence.split()), font_size, page_number))
                conn.commit()

# Close the database connection
conn.close()
