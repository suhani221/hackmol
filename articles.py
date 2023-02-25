from urllib.request import urlopen, Request
from bs4 import BeautifulSoup

def get_article_links(tags, years, months, num_articles):
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
    
    return article_links