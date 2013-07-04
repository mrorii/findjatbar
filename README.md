# findjatbar

[jatbar.com](http://www.jatbar.com/) (Jason and Terry's Bay Area Review)
was a very useful restaurant review site for the Bay Area.
Unfortunately, this site was closed in 2009.

Let's see if Jason and Terry aren't hiding in [Yelp](http://www.yelp.com/) by using machine learning and authorship identification.

## Requirements

Python 2.7 is required. Install dependencies with:

    pip install -r requirements.txt

## Step 1: crawl Jason and Terry's reviews from the Internet Archive

Obtain a list of restaurants stored in Jatbar.

    mkdir crawl-jatbar
    python findjatbar/get_restaurants.py > restaurants.txt


## Step 2: crawl Yelp reviews

Yelp doesn't currently have a full API to retrieve reviews, so we are forced to crawl.
We need to first find out the corresponding Yelp URL for the each of the restaurants on Jatbar.

    python findjatbar/find_corresponding_yelp_urls.py < restaurants.txt > yelp_urls.txt

## Step 3: train and test

TODO
