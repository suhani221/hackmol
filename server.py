import os
from flask import Flask, request
import os
import hashlib
from PIL import Image
import fitz #PyMuPDF
import io
import io
import base64
from get_youtube_links import *
from articles import *

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    final_response = {}
    # Check if a file was submitted in the form data
    if 'file_upload' not in request.files:
        return 'No file found in request', 400
    
    file = request.files['file_upload']
    
    # Check if the file is a PDF
    if file.mimetype != 'application/pdf':
        return 'Invalid file format. Only PDF files are accepted.', 400
    
    # Save the file to a specified folder
    folder_path = '/Users/suhaniagarwal/Desktop/hackmol'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    file.save(os.path.join(folder_path, file.filename))
    
    pdf_file_name = file.filename

    scrape(pdf_file_name)

    response = extract_and_detect(pdf_file_name)
    headings = getAllHeadings(pdf_file_name)
    contents = getAllContent(pdf_file_name)
    youtube_links = getVideoLinks(pdf_file_name)
    notes_queries = getAllNotesQueries(pdf_file_name)

    tags = ["GPT"]
    years = ['2019']
    months = ['06']
    article_query = get_article_links(tags, years, months, num_articles=2)

    final_response['headings'] = headings
    final_response['images'] = response
    final_response['contents'] = contents
    final_response['youtube_links'] = youtube_links
    final_response['topic'] = headings[0]
    final_response['notes_queries'] = notes_queries
    final_response['article_query'] = article_query

    jsonify(headings)
    return final_response

def extract_and_detect(pdf_file_name):
    folder_name = pdf_file_name.split(".")[0]
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    pdf_file = fitz.open(pdf_file_name)
    saved_hashes = set()
    results = []
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
                with open(filename, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                    results.append({
                        "img": encoded_string,
                        "references": []
                    })

    from google.cloud import vision
    client = vision.ImageAnnotatorClient()
    for image_obj in results:
        image = Image.open(io.BytesIO(base64.b64decode(image_obj['img'])))
        with io.BytesIO() as output:
            image.save(output, format="PNG")
            content = output.getvalue()
        image = vision.Image(content=content)
        response = client.web_detection(image=image)
        annotations = response.web_detection
        urls = []
        if annotations.pages_with_matching_images:
            for page in annotations.pages_with_matching_images:
                urls.append(page.url)
        urls = urls[:3] # take the top 3 urls
        image_obj['references'] = urls

    return results

if __name__=='__main__':
   app.debug = True
   app.run()