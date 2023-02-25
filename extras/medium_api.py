import json
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request

#------------------------INPUTS-----------------------------------------------#

# to generalize this scraper for later use - EDIT THIS to suit your purposes
# keep all list items strings, or else this doesn't work
tags = ["JSON"] #tags to scrape
years = ['2020'] #years to scrape during
months = ['06'] #months to scrape during (every available day within the month will be scraped)
jsonName = "medium.json" #name of the output file

# don't touch unless you need to
hdr = {'User-Agent': 'Mozilla/5.0'}

#------------------------SCRAPER FUNCTIONS------------------------------------#

# INPUT - components needed to get the start link
# OUTPUT - the links of all the articles in the tag in the date range
def scrapeLinksToArticles(tag, years, months):
    startLink = "https://medium.com/tag/"+tag+"/archive/"
    articleLinks = []
    for y in years:
        yearLink = startLink + y
        for m in months:
            monLink = yearLink + "/" + m
            # open the month link and scrape all valid days (days w/ link) into drive
            req = Request(monLink, headers=hdr)
            page = urlopen(req)
            monSoup = BeautifulSoup(page)
            try: # if there are days
                allDays = list(monSoup.find("div", {"class": "col u-inlineBlock u-width265 u-verticalAlignTop u-lineHeight35 u-paddingRight0"}).find_all("div", {"class":"timebucket"}))
                for a in allDays:
                    try: # try to see if that day has a link
                        dayLink = a.find("a")['href']
                        req = Request(dayLink, headers=hdr)
                        page = urlopen(req)
                        daySoup = BeautifulSoup(page)
                        links = list(daySoup.find_all("div", {"class": "postArticle-readMore"}))
                        for l in links:
                            articleLinks.append(l.find("a")['href'])
                    except: pass
            except: # take the month's articles
                links = list(monSoup.find_all("div", {"class": "postArticle-readMore"}))
                for l in links:
                    articleLinks.append(l.find("a")['href'])
                print("issueHere")
    print("Article Links: ", len(articleLinks))
    return articleLinks

# INPUT - link to a medium article
# OUTPUT - dictionary with article title and link
def scrapeArticle(link):
    req = Request(link, headers=hdr)
    page = urlopen(req)
    soup = BeautifulSoup(page)
    
    try:
        title = soup.find("h1", {"class": "graf graf--h2 graf-after--figure graf--title"}).get_text()
    except AttributeError:
        title = "ERROR: Could not find article title"
    
    article = {"title": title, "link": link}
    return article

#------------------------PROCESS----------------------------------------------#

articles = []
for tag in tags:
    articleLinks = scrapeLinksToArticles(tag, years, months)
    for art in articleLinks:
        articles.append(scrapeArticle(art))

# write the data to a JSON file
with open(jsonName, "w") as outfile:
    json.dump(articles, outfile, indent=4)

print("Scraping complete!")
