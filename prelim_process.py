__author__ = 'Xun'

import urllib2
from bs4 import BeautifulSoup
import unicodecsv
import pandas as pd
import numpy as np
import time
import re

# This function is designed to extract the links for the top spots in each city #
# Output contains a list of spot links #
def gettopspot(link):
    # Internet Connection and Reading webpage in#
    url = urllib2.urlopen(link)
    webdoc = url.read()
    tree = BeautifulSoup(webdoc)
    url.close()

    # Read in important data element #
    prolinks = tree.find_all('div', class_='property_title')

    spotlink = dict()

    i=0
    for item in prolinks:
        if item.find('a').get('href').find('Attraction_Review') >0 : # Make sure the item belongs to a real spot
            spotlink[i] = item.find('a').get('href')
            i=i+1

    return spotlink

#This function is designed to be universal for scraping review text from TripAdvisor #
def getreviews(link):
    # Internet Connection and Reading webpage in#
    url = urllib2.urlopen(link)
    webdoc = url.read()
    tree = BeautifulSoup(webdoc)
    url.close()

    # Variables initiation and preparation #
    spotText = dict()
    titleText = dict()
    reviewText = dict()
    reviewStar = dict()
    reviewDate = dict()
    reviewerGeo = dict()
    reviewerLevel = dict()
    reviewerTotal = dict()
    reviewerAttTotal = dict()
    reviewerHelpful = dict()

    # Read in important data element #
    review = tree.find_all('div',class_=re.compile("inlineReviewUpdate"))
    spotname = tree.title.string.split(' (')[0]

    i=0
    for item in review:
        spotText[i] = spotname
        reviewStar[i] = item.find('span', class_='rate sprite-rating_s rating_s').find('img').get('alt')[0]
        reviewDate[i] = item.find('span', class_='ratingDate').getText()[9:]
        titleText[i] = item.find('span',class_='noQuotes').getText()
        reviewText[i] = item.find('p', class_='partial_entry').getText()

        # For Reviewer Section, Use conditional processing for Content Checking
        if item.find('div', class_='location'):
            reviewerGeo[i] = item.find('div', class_='location').getText()
        else:
            reviewerGeo[i] = 'N/A'
        if item.find('div', class_=re.compile("levelBadge")):
            reviewerLevel[i] = item.find('div', class_=re.compile("levelBadge")).get('class')[2]
        else:
            reviewerLevel[i] = 'N/A'
        if item.find('div', class_='reviewerBadge badge'):
            reviewerTotal[i] = item.find('div', class_='reviewerBadge badge').find('span', class_='badgeText').getText()
        else:
            reviewerTotal[i] = 'N/A'
        if item.find('div', class_='contributionReviewBadge badge'):
            reviewerAttTotal[i] = item.find('div', class_='contributionReviewBadge badge').find('span', class_='badgeText').getText()
        else:
            reviewerAttTotal[i] = 'N/A'
        if item.find('div', class_=re.compile("helpfulVotesBadge")):
            reviewerHelpful[i] = item.find('div', class_=re.compile("helpfulVotesBadge")).find('span', class_='badgeText').getText()
        else:
            reviewerHelpful[i] = 'N/A'
        i=i+1

    # Final Data Restructure #
    spotSr = pd.Series(spotText)
    titleSr = pd.Series(titleText)
    reviewSr = pd.Series(reviewText)
    ratingSr = pd.Series(reviewStar)
    dateSr = pd.Series(reviewDate)
    geoSr = pd.Series(reviewerGeo)
    levelSr = pd.Series(reviewerLevel)
    totalSr = pd.Series(reviewerTotal)
    attTotalSr = pd.Series(reviewerAttTotal)
    helpfulSr = pd.Series(reviewerHelpful)
    spotReview = pd.DataFrame({'Spot':spotSr, 'Title':titleSr, 'Review':reviewSr, 'Rating':ratingSr, 'Date':dateSr,
                               'Origin':geoSr, 'Level':levelSr, 'Total':totalSr, 'Attraction':attTotalSr, 'Helpful':helpfulSr})

    return spotReview


spotlinks = gettopspot('http://www.tripadvisor.com/Attractions-g187791-Activities-Rome_Lazio.html')

# Create huge List #
superlist = list()
pagemin=0
pagemax=50 # Scrape reviews up to 25 pages
spotindexmin = 0
# Select up to 15 spots if possible
if len(spotlinks) > 15:
    spotindexmax = 15
else:
    spotindexmax = len(spotlinks)
# Automatically Construct all links
for spot in range(spotindexmin,spotindexmax):
    for page in range(pagemin, pagemax):
        link=spotlinks[spot]
        tempindex = link.find('-Reviews-') + len('-Reviews-')
        link = 'http://www.tripadvisor.com'+spotlinks[spot][:tempindex]+'or'+str(page)+'0-'+spotlinks[spot][tempindex:]
        superlist.append(link)

# Call function and generate DataFrame output #
# Initiate output file #
review = getreviews(superlist[0])
with open('reviews.csv', 'wb') as f:
        review.to_csv(f, header=False,encoding='utf-8', index=False)
f.close()
print 'Output File Created'

count=2
for link in superlist[1:]:
    review = getreviews(link)
    print 'Finish '+link
    time.sleep(2)
    # Write data to csv file #
    with open('reviews.csv', 'ab') as f:
        review.to_csv(f, header=False, encoding='utf-8', index=False)
    f.close()
    print 'Record '+str(count)+' Created'
    count=count+1
    time.sleep(3)
