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

#gets all the heading as a list
def getHeadingList(pdf_file_name):
    num_pages = getNumberOfPages(pdf_file_name)
    heading_list = []
    for i in range(1, num_pages):
        heading = getHeading(pdf_file_name, i)
        heading_text = heading[0][0].replace(" ", "-")  # replace spaces with hyphens
        heading_list.append(heading_text)
    return heading_list


headings_final=getHeadingList(pdf_file_name)
# print(headings_final)

def get_article_links(tags, years, months, num_articles=1):
    hdr = {'User-Agent': 'Mozilla/5.0'}
    start_link = "https://medium.com/tag/{}/archive/"
    article_links = []
    
    for tag in tags: 
        for year in years:
            year_link = start_link.format(tag) + year
            for month in months:
                mon_link = year_link + "/" + month
                
                req = Request(mon_link, headers=hdr)
                page = urlopen(req)
                mon_soup = BeautifulSoup(page, 'html.parser')
                
                try:
                    all_days = mon_soup.find("div", {"class": "col u-inlineBlock u-width265 u-verticalAlignTop u-lineHeight35 u-paddingRight0"}).find_all("div", {"class":"timebucket"})
                    for day in all_days:
                        try:
                            day_link = day.find("a")['href']
                            req = Request(day_link, headers=hdr)
                            page = urlopen(req)
                            day_soup = BeautifulSoup(page, 'html.parser')
                            links = day_soup.find_all("div", {"class": "postArticle-readMore"})
                            for link in links:
                                article_links.append(link.find("a")['href'])
                                if len(article_links) == num_articles:
                                    break
                            if len(article_links) == num_articles:
                                break
                        except:
                            pass
                    if len(article_links) == num_articles:
                        break
                except:
                    links = mon_soup.find_all("div", {"class": "postArticle-readMore"})
                    for link in links:
                        article_links.append(link.find("a")['href'])
                        if len(article_links) == num_articles:
                            break
                    if len(article_links) == num_articles:
                        break
                        
            if len(article_links) == num_articles:
                break
                
    out_put_text = "\n".join(article_links)
    
    return out_put_text

tags = [headings_final[0]]
# print(tags)
years = ['2019','2021']
months = ['06']

article_links = get_article_links(tags, years, months, num_articles=1)
print(article_links)

