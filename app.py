import os
import hashlib
from PIL import Image
import fitz #PyMuPDF
import io
import io
import base64

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def extract_and_detect():
    pdf_file_name = "W01_L1_Intro_SR.pdf"
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
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)

