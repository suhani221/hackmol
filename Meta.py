from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import os

#ORC- need handwritten notes
def detect_texts_directory(directory):
    """Detects text in all images in a directory."""
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
            response = client.text_detection(image=image)
            texts = response.text_annotations
            if len(texts) > 0:
                block_text = texts[0].description
                word_list = block_text.split()
                sentence = ' '.join(word_list)
                results[filename] = sentence
    return results
directory = 'handwritten_notes'
results = detect_texts_directory(directory)
print(results)

#IMAGE LINKS- Need extracted images
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
            results[filename] = urls
    return results
directory = 'extracted_images'
results = detect_web_directory(directory)
print(results)

#ARTICLE LINKS-need headings as tags
def get_article_links(tags, years, months, num_articles=2):
    hdr = {'User-Agent': 'Mozilla/5.0'}
    start_link = "https://medium.com/tag/{}/archive/"
    article_links = {}
    
    for tag in tags: 
        tag_links = []
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
                                tag_links.append(link.find("a")['href'])
                                if len(tag_links) == num_articles:
                                    break
                            if len(tag_links) == num_articles:
                                break
                        except:
                            pass
                    if len(tag_links) == num_articles:
                        break
                except:
                    links = mon_soup.find_all("div", {"class": "postArticle-readMore"})
                    for link in links:
                        tag_links.append(link.find("a")['href'])
                        if len(tag_links) == num_articles:
                            break
                    if len(tag_links) == num_articles:
                        break
                        
            if len(tag_links) == num_articles:
                break
                
        article_links[tag] = tag_links
    
    return article_links
tags = ["GPT-3", "Python", "Data Science"]
years = ['2022']
months = ['01']
article_links = get_article_links(tags, years, months, num_articles=2)
print(article_links)