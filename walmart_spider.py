from urllib2 import urlopen
from bs4 import BeautifulSoup
import re
from sys import argv
from time import sleep

#This code scraps data from walmart's website for searches of both cereal and cold cereal and write them to csv formatted files called cereal and cold_cereal respectively. The data is appended to the files so that multiple runs can be done to gather continuous data for different days. To start the data collection over delete the data from the output file and save.

script, cereal, cold_cereal = argv

#Function to create beautifulsoup object from a page's url to allow parsing. If the server denies a request, the function waits 30 seconds and retires. If after 10 tries, the request is still being rejected, the program will end with an error message. 

def soupit(html):
    for tries in range(10):
        try:
             soup = BeautifulSoup(urlopen(html).read(),'html.parser')
             break
        except:
            sleep(30)
            print 'Sleeping for 30 seconds before next link'
            pass
   
    return soup


#This is the link gathering function. Links gathered will later be looped through to get data. The arguments are Walmart's base url for the seach as well as the array 'pages' which list the urls of each search result page after the first.

def get_page_links(base,pages):
    
    #Initialize the array where all cereal links will be stored.
    links = [] 
     
    #For each page, find the href of each of it's 20 links (for walmart searches) and store in 'links'.
    for page in pages:
        soup = soupit(page)
        Class = soup.find_all('a', class_= 'js-product-title')
        for link in Class:

            links.append('http://www.walmart.com' + link['href'])
    
    return links

#This function gathers all data required, including Rank, Relavant Brand Name (or else 'Other'), the Rating (as rated by walmart.com shoppers out of 5 stars. The lowest possible rating is a 1. If there are no ratings, the value 'None' is used) and Number of Reviews. The data is appended to a csv file in the respective order just listed.

#Note! Certain product links lead to products that have no Reviews or Ratings which will be named 'Bundles'. Generally, 'Bundles' are a bundle of multiple items which can be bought at a discount with choices between which items to include. A value of 'Bundle' in the Review and Rating columns of the output file still has a Brand name and Ranking.

def get_data(link):
    
    soup = soupit(link)
    
    #Get the Brand name
    text = soup.find('div', class_ = 'js-ellipsis module')
    try:
        heading = soup.find('h1', itemprop = 'name').find('span')
    except AttributeError:
        try:
            heading = soup.find('h1', class_ = 'heading-b product-name product-heading js-product-heading')
        except AttributeError:
            pass
        pass
        
    title = heading.string
    
    try:
        string = text.get_text()
        
    except AttributeError:
        string = str(text)
        
    p = re.compile('Kellogg|Cheerio|Kashi|Post |Post\'s')
    s = p.search(string)
    t = p.search(title)
    if s or t:
        try:
            cereal.write(',' + s.group(0))
        except AttributeError:
            cereal.write(',' + t.group(0))
    else:
        cereal.write(',Other')

    #Get the star rating            
    try:
        rating = soup.find('span', itemprop = 'ratingValue')
        star = rating.find('span')
        stars = star.string
        for i in stars.split():
            try:
                a = float(i)
                if a == 0.0:
                    cereal.write(',None,')
                else:
                    cereal.write(',' + str(a) + ',')
            
                break
            except ValueError:
                continue
    except AttributeError:
        cereal.write(',Bundle,')   
        
    #Get the number of reviews   
    review = soup.find('span', itemprop = 'ratingCount')      
    try:
        result = review.string
        
    except AttributeError:
        try:
            parent = soup.find('div', class_ = 'product-subhead-section product-subhead-reviews-count')
            review = parent.find('a', class_ = 'js-product-anchor')
            result = review.string
        except AttributeError:
            cereal.write('Bundle\n')

    try:        
        for i in result.split():
            try:
                a = float(i)
                if a == 0.0 :
                    cereal.write('0\n')
                else:
                    cereal.write(str(a) + '\n')
            
                break
            except ValueError:
                continue
    except:
        pass


#First we get data for the 'cereal' search
cereal = open(cereal, 'a')

base = 'http://www.walmart.com/search/?query=cereal&cat_id=0'

#Initialize the 50 pages in walmart's cereal search
pages = [base]
for page in range(2,51):
        
    current = 'http://www.walmart.com/search/?query=cereal&page=%d&cat_id=0' % page
    pages.append(current)
    
links = get_page_links(base,pages)

rank = 0

for link in links:
    rank += 1
    cereal.write(str(rank))
    get_data(link)

cereal.close()


#Now we get data for the 'cold cereal' search
cereal = open(cold_cereal, 'a')

base = 'http://www.walmart.com/search/?query=cold%20cereal&cat_id=0'

#Initialize the 39 pages in walmart's cold cereal search
pages = [base]
for page in range(2,40):
        
    current = 'http://www.walmart.com/search/?query=cold%%20cereal&page=%d&cat_id=0' % page
    pages.append(current)

links = get_page_links(base,pages)

rank = 0

for link in links:
    rank += 1
    cereal.write(str(rank))
    get_data(link)
    
cereal.close()


#Written by: Adrien Green

