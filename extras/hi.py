from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar
import csv
with open('hi.csv', mode='w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['Sentence', 'Font Size'])
    for page_layout in extract_pages("W03_L2_Query_languages_1.pdf"):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                sentence = ""
                font_size = None
                for text_line in element:
                    # Check for bullet points
                    if text_line.get_text().strip().startswith(("-", "•", "*")):
                        if sentence:
                            writer.writerow([sentence, font_size])
                            sentence = ""
                            font_size = None
                        # Add a space after the bullet point
                        sentence = text_line.get_text().strip()[0] + ' ' + text_line.get_text().strip()[1:]
                        font_size = round(text_line[0].size)
                        writer.writerow([sentence, font_size])
                        sentence = ""
                        font_size = None
                    else:
                        for character in text_line:
                            if isinstance(character, LTChar):
                                if font_size is None:
                                    font_size = round(character.size)
                                if character.get_text().strip():
                                    sentence += character.get_text() + ' '
                                else:
                                    if sentence:
                                        writer.writerow([sentence.strip(), font_size])
                                    sentence = ""
                                    font_size = None
                if sentence:
                    writer.writerow([sentence.strip(), font_size])
