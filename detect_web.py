def detect_web(path):
    """Detects web annotations given an image."""
    from google.cloud import vision
    import io
    client = vision.ImageAnnotatorClient()
    with io.open(path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.web_detection(image=image)
    annotations = response.web_detection
    urls = [] # list to store page urls
    if annotations.pages_with_matching_images:
        for page in annotations.pages_with_matching_images:
            urls.append(page.url)
    # take the top 5 urls
    urls = urls[:5]
    # return the URLs as a string
    return '\n'.join(urls)
path='image17_1.jpeg'
print(detect_web(path))
