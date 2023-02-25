import os
import hashlib
from PIL import Image
import fitz #PyMuPDF
import io
import base64

pdf_file_name = "W01_L1_Intro_SR.pdf"

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

def detect_web_directory(directory):
    """Detects web annotations for all images in a directory."""
    from google.cloud import vision
    import io
    client = vision.ImageAnnotatorClient()
    results = {}
    for filename in os.listdir(directory):
        if filename.endswith('.jpeg') or filename.endswith('.jpg') or filename.endswith('.png'):
            path = os.path.join(directory, filename)
            with io.open(path, 'rb') as image_file:
                content = image_file.read()
            image = vision.Image(content=content)
            response = client.web_detection(image=image)
            annotations = response.web_detection
            urls = []
            if annotations.pages_with_matching_images:
                for page in annotations.pages_with_matching_images:
                    urls.append(page.url)
            urls = urls[:3] # take the top 3 urls
            with open(path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            results[filename] = {
                "image_base64": encoded_string,
                "references": urls
            }
    return results

# Extract images from PDF
extractImages(pdf_file_name)

# Detect web annotations for images and store in JSON format
directory = pdf_file_name.split(".")[0]
results = detect_web_directory(directory)
print(results)
