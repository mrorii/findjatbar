# findjatbar

[jatbar.com](http://www.jatbar.com/) (Jason and Terry's Bay Area Review)
was a very useful restaurant review site for the Bay Area.
Unfortunately, this site was closed in 2009 :cry:.

Let's see if Jason and Terry aren't hiding in [Yelp](http://www.yelp.com/)
by using machine learning.

## Requirements

Python 2.7 is required. Install dependencies with:

    pip install -r requirements.txt

## Step 1: scrape Jason and Terry's reviews from the Internet Archive

Obtain a list of restaurants stored in Jatbar.

    mkdir output
    python findjatbar/get_restaurants.py > output/restaurants.txt

Scrape Jason and Terry's reviews given the list of restaurants:

    python findjatbar/scrape_jatbar_reviews.py < output/restaurants.txt \
                                               > output/jatbar_reviews.json


## Step 2: scrape Yelp reviews

Yelp doesn't currently have a full API to retrieve reviews, so we must scrape them.
We need to first find out the corresponding Yelp URL for the each of the restaurants on Jatbar:

    python findjatbar/find_corresponding_yelp_urls.py < output/restaurants.txt \
                                                      > output/yelp_urls.txt

We can then scrape the Yelp reviews.
For simplicity, we only scrape the reviews on the first page of a venue.

    python findjatbar/scrape_yelp_reviews.py < output/yelp_urls.txt \
                                             > output/yelp_reviews.json

## Step 3: train and test

We first combine both types of reviews into one file:

    cat output/yelp_reviews.json output/jatbar_reviews.json > output/reviews.json

We next split all of the reviews into the train, dev, and test set.
Here, we must specify whose review we want to classify as positive:
this can be `Jason`, `Terry`, or `Both`.

    python findjatbar/split_data.py output/reviews.json Jason output --seed 123

Finally, we train a classifier, tune it on the dev set, and test:

    python findjatbar/classify.py output


## Acknowledgements

This project is heavily influenced by the following repository:

* word-salad: https://github.com/vchahun/word-salad
