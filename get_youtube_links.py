import sqlite3
import requests
from bs4 import BeautifulSoup
import os
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
import os

def databaseName(pdf_file_name):
    database_name = pdf_file_name.split('.')
    database_name = database_name[0] + '.db'
    return database_name

def create_table(database_name):
    conn = sqlite3.connect(database_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS pdf_sentences
                (sentence TEXT,
                 font_size INTEGER,
                 page_number INTEGER)''')
    conn.commit()
    conn.close()

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

def getNumberOfPages(pdf_file_name):
    pdf_file = fitz.open(pdf_file_name)
    num_pages = pdf_file.page_count
    return num_pages

def getHeading(pdf_file_name, page_number):
    database_name = databaseName(pdf_file_name)
    conn = sqlite3.connect(database_name)
    c = conn.cursor()
    c.execute("SELECT sentence FROM pdf_sentences WHERE page_number = ? AND font_size = (SELECT MAX(font_size) FROM pdf_sentences WHERE page_number = ?)", (page_number, page_number))
    results = c.fetchall()
    conn.close()
    return results

# get all the headings as list
def getAllHeadings(pdf_file_name):
    page_nums = getNumberOfPages(pdf_file_name)
    headings = []
    for i in range(1, page_nums+1):
        heading = getHeading(pdf_file_name, i)
        headings.append(heading[0][0])
    return headings

def getPageContent(pdf_file_name, page_number):
    database_name = databaseName(pdf_file_name)
    conn = sqlite3.connect(database_name)
    c = conn.cursor()
    c.execute("SELECT sentence FROM pdf_sentences WHERE page_number = ? AND font_size NOT IN (SELECT MAX(font_size) FROM pdf_sentences WHERE page_number = ? GROUP BY page_number)", (page_number, page_number))
    results = c.fetchall()
    conn.close()
    return results

# def getAllContent(pdf_file_name):
#     page_nums = getNumberOfPages(pdf_file_name)
#     contents = []
#     for i in range(1, page_nums+1):
#         content = getPageContent(pdf_file_name, i)
#         final_content = ''
#         for j in content:
#             contents.append(content[0][0])
#     return contents

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

def getAllNotesQueries(pdf_file_name):
    page_nums = getNumberOfPages(pdf_file_name)
    queries = []
    for i in range(1, page_nums+1):
        heading_query, content_query, combined_query = makeQuery(pdf_file_name, i)
        queries.append(combined_query)
    return queries

def getAllContent(pdf_file_name):
    page_nums = getNumberOfPages(pdf_file_name)
    contents = []
    for i in range(1, page_nums+1):
        content = getPageContent(pdf_file_name, i)
        final_content = ''
        for j in content:
            final_content += j[0] + ' '
        contents.append(final_content)
    return contents

def getYouTubeVideos(query):
    modified_query = query.replace(' ', '+')
    url = 'https://www.youtube.com/results?search_query=' + modified_query
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    with open('youtube.html', 'w') as f:
        f.write(soup.prettify())
    youtube_url = "https://www.youtube.com"
    with open('youtube.html') as f:
        html = f.read()
    lines = html.split('"')
    links = []
    for line in lines:
        if "/watch?v=" in line:
            line = youtube_url + line
            links.append(line)

    youtube_links = []

    for link in links:
        link = link.split('\\')[0]
        if link not in youtube_links:
            youtube_links.append(link)

    os.remove('youtube.html')
    return youtube_links

def get_video_transcript(video_id):
    try:
        srt = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = ""
        for i in srt:
            transcript += i['text'] + " "
        return transcript
    except:
        return ""
        
def cosine_similarity(text1, text2):
    
    if text1 == "" or text2 == "":
        return 0

    tokens1 = text1.lower().split()
    tokens2 = text2.lower().split()

    unique_tokens = set(tokens1 + tokens2)
    tf1 = Counter(tokens1)
    tf2 = Counter(tokens2)

    idf = {}
    for token in unique_tokens:
        count = sum(1 for text in [tokens1, tokens2] if token in text)
        idf[token] = math.log((2 + 1) / (count + 1)) + 1

    tfidf1 = [tf1[token] * idf[token] for token in unique_tokens]
    tfidf2 = [tf2[token] * idf[token] for token in unique_tokens]

    similarity_score = sum(a * b for a, b in zip(tfidf1, tfidf2)) / (math.sqrt(sum(a ** 2 for a in tfidf1)) * math.sqrt(sum(b ** 2 for b in tfidf2)))

    return similarity_score

def get_best_video(query, youtube_links):
    transcript = get_video_transcript(youtube_links[0].split('=')[1])
    similarity_score = cosine_similarity(query, transcript)
    best_video = youtube_links[0]
    for link in youtube_links:
        new_transcript = get_video_transcript(link.split('=')[1])
        score = cosine_similarity(query, new_transcript)
        if score > similarity_score:
            similarity_score = score
            best_video = link
    return best_video

def get_response_from_api(content):
    # Set the URL to the API endpoint
    url = "https://chatur-notes.onrender.com/"

    # Define the JSON data to be sent in the request body
    data = {"content": content}

    # Convert the data to JSON format
    json_data = json.dumps(data)

    # Set the headers for the request
    headers = {"Content-Type": "application/json"}
    # Make the POST request with the JSON data and headers
    response = requests.post(url, data=json_data, headers=headers)
    text = response.text
    text = text.replace('\n', ' ')
    return text

def getVideo(pdf_file_name, page_number):
    heading_query, content_query, combined_query = makeQuery(pdf_file_name, page_number)
    relevancy_gpt = get_response_from_api(combined_query)
    relevancy_query = heading_query + " " + content_query
    youtube_links = getYouTubeVideos(relevancy_query)
    best_video = get_best_video(relevancy_gpt, youtube_links[0:5])
    return best_video

def getVideoLinks(pdf_file_name):
    scrape(pdf_file_name)
    num_pages = getNumberOfPages(pdf_file_name)
    video_links = []
    for i in range(1, num_pages):
        video_links.append(getVideo(pdf_file_name, i))
        print(len(video_links))
    return video_links