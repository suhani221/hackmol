import sqlite3
import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
from collections import Counter
import math
import fitz
import sqlite3
import json
import fitz #PyMuPDF
import io
from PIL import Image
import hashlib
from urllib.request import urlopen, Request
import os

pdf_file_name = "W01_L1_Intro_SR.pdf"
#creates database and take pdf as argument
def databaseName(pdf_file_name):
    database_name = pdf_file_name.split('.')
    database_name = database_name[0] + '.db'
    return database_name
#creates database table 
def create_table(database_name):
    conn = sqlite3.connect(database_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS pdf_sentences
                (sentence TEXT,
                 font_size INTEGER,
                 page_number INTEGER)''')
    conn.commit()
    conn.close()
#scrapes pdf and stores in database
def scrape(pdf_file_name):
    database_name = databaseName(pdf_file_name)
    create_table(database_name)
    conn = sqlite3.connect(database_name)
    c = conn.cursor()
    pdf = fitz.open(pdf_file_name) # filePath is a string that contains the path to the pdf
    for pageNum, page in enumerate(pdf):
        dict = page.get_text("dict")
        blocks = dict["blocks"]
        for block in blocks:
            if "lines" in block.keys():
                spans = block['lines']
                for span in spans:
                    data = span['spans']
                    for lines in data:
                        sentence = lines['text']
                        #strip the sentence of any leading or trailing whitespace
                        sentence = sentence.strip()
                        #drop sentences that are empty strings or contain only whitespace or newlines or tabs or length 1
                        font_size = round(lines['size'])
                        if sentence == '' or sentence == ' ' or len(sentence) == 1:
                            continue
                        c.execute("INSERT INTO pdf_sentences (sentence, font_size, page_number) VALUES (?, ?, ?)", (sentence, font_size, pageNum+1))
                        conn.commit()
    conn.close()
scrape(pdf_file_name)

#gets number of pages by taking the pdf
def getNumberOfPages(pdf_file_name):
    pdf_file = fitz.open(pdf_file_name)
    num_pages = pdf_file.page_count
    return num_pages

#gets all the heading
def getHeading(pdf_file_name, page_number):
    database_name = databaseName(pdf_file_name)
    conn = sqlite3.connect(database_name)
    c = conn.cursor()
    c.execute("SELECT sentence FROM pdf_sentences WHERE page_number = ? AND font_size = (SELECT MAX(font_size) FROM pdf_sentences WHERE page_number = ?)", (page_number, page_number))
    results = c.fetchall()
    conn.close()
    return results

#gets all the content
def getPageContent(pdf_file_name, page_number):
    database_name = databaseName(pdf_file_name)
    conn = sqlite3.connect(database_name)
    c = conn.cursor()
    c.execute("SELECT sentence FROM pdf_sentences WHERE page_number = ? AND font_size NOT IN (SELECT MAX(font_size) FROM pdf_sentences WHERE page_number = ? GROUP BY page_number)", (page_number, page_number))
    results = c.fetchall()
    conn.close()
    return results

#gets the combined query that fuels notes and chatgpt prompt and youtube engine
def makeQuery(pdf_file_name, page_number):
    content = getPageContent(pdf_file_name, page_number)
    heading = getHeading(pdf_file_name, page_number)
    content_query = ''
    heading_query = ''
    for i in range(len(content)):
        content_query += content[i][0] + ' '
    for i in range(len(heading)):
        heading_query += heading[i][0] + ' '
    combined_query = "The slide topic is " + heading_query + " and the contents of the slides are " + content_query + "\nmake me brief study notes for this slide" 
    return heading_query, content_query, combined_query

#gets the extracted dimag
def extractImages(pdf_file_name):
    folder_name = pdf_file_name.split(".")[0]
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    pdf_file = fitz.open(pdf_file_name)
    saved_hashes = set()
    for page_index in range(len(pdf_file)):
        page = pdf_file[page_index]
        image_list = page.get_images()
        for image_index, img in enumerate(image_list, start=1):
            xref = img[0]
            base_image = pdf_file.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_hash = hashlib.md5(image_bytes).hexdigest()
            if image_hash not in saved_hashes:
                image = Image.open(io.BytesIO(image_bytes))
                filename = f"{folder_name}/image{page_index+1}_{image_index}.{image_ext}"
                image.save(open(filename, "wb"))
                saved_hashes.add(image_hash)