import requests 
from bs4 import BeautifulSoup
import csv 
from selenium import webdriver
import time
import sys
import argparse

pathToReviews = "TripReviews.csv"
pathToStoreInfo = "TripStoresInfo.csv"

def scrapeRestaurantsUrls(tripURLs):
    urls =[]
    for url in tripURLs:
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        results = soup.find('div', class_='_1kXteagE')
        stores = results.find_all('div', class_='wQjYiB7z')
        for store in stores:
            unModifiedUrl = str(store.find('a', href=True)['href'])
            urls.append('https://www.tripadvisor.com'+unModifiedUrl)            
    return urls

def scrapeRestaurantInfo(url):
    driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver") 
    driver.get(url)
    content = driver.page_source
    soup = BeautifulSoup(content)
    res = soup.find('div', class_='page')
    storeName = res.find('h1', class_='fkWsC b d Pn').text
    print(storeName)
    avgRating = res.find('span', class_='bvcwU P').text
    print(avgRating)
    # storeAddress = res.find('div', class_= 'eWZDY _S eCdbd yYjkv') #
    storeAddress = res.find('span', class_='ceIOZ yYjkv').text
    print(storeAddress)
    # noReviews = soup.find('a', class_='_10Iv7dOs').text.strip().split()[0]
    noReviews = soup.find('span', class_='cdKMr Mc _R b').text.strip().split()[0]
    print(noReviews)
    with open(pathToStoreInfo, mode='a', encoding="utf-8") as trip:
        data_writer = csv.writer(trip, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
        data_writer.writerow([storeName, storeAddress, avgRating, noReviews])

parser = argparse.ArgumentParser()
parser.add_argument('--url', required=True, help ='need starting url')
parser.add_argument('-i', '--info', action='store_true', help="Collects restaurant's info")
parser.add_argument('-m', '--many', action='store_true', help="Collects whole area info")
args = parser.parse_args()
startingUrl = args.url 
if args.info:
    info = True
else:
    info = False
if args.many:
    urls = scrapeRestaurantsUrls([startingUrl])
else:
    urls = [startingUrl]

driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")

for url in urls:
    print(url)
    if info == True:
        scrapeRestaurantInfo(url)

    nextPage = True
    while nextPage:
        driver.get(url)
        time.sleep(1)
        more = driver.find_elements_by_xpath("//span[contains(text(),'More')]")
        for x in range(0,len(more)):
            try:
                driver.execute_script("arguments[0].click();", more[x])
                time.sleep(3)
            except:
                pass
        driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver") 
        driver.get(url)
        content = driver.page_source
        soup = BeautifulSoup(content,features="lxml")
        res = soup.find('div', class_='page')
        hotelname = res.find('h1',class_='fkWsC b d Pn').text
        try:
            reviews = res.find_all('div', class_='cWwQK MC R2 Gi z Z BB dXjiy')
        except Exception:
            continue
        try:
            with open(pathToReviews, mode='a', encoding="utf-8") as trip_data:
                data_writer = csv.writer(trip_data, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
                for review in reviews:
                    date = review.find('span', class_='euPKI _R Me S4 H3').text # date of stay
                    headline = review.find('div', class_='fpMxB MC _S b S6 H5 _a').text
                    descrip = review.find('q',class_='XllAv H4 _a').text # customer review
                    name = review.find('a', class_='ui_header_link bPvDb').text
                    data_writer.writerow([hotelname, name, date, headline, descrip])
        except:
            pass
        try:
            unModifiedUrl = res.find('a', class_='pageNum')['href']
            url = 'https://www.tripadvisor.com/' + unModifiedUrl
            print(url)
        except:
            nextPage = False
