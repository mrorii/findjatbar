# findjatbar

[jatbar.com](http://www.jatbar.com/) (Jason and Terry's Bay Area Review)
was a legendary restaurant review site for the Bay Area.
Unfortunately, the website was closed in 2009 :cry:.

Let's see if Jason and Terry aren't hiding on [Yelp](http://www.yelp.com/)
by using machine learning.
We'll create models to determine whether a review is written by Jason or Terry.

## Requirements

Python 2.7 is required. Install dependencies with:

    pip install -r requirements.txt

## Step 1: scrape Jason and Terry's reviews from the Internet Archive

Obtain a list of restaurants stored in Jatbar.

    mkdir output
    python findjatbar/get_restaurants.py > output/jatbar_restaurants.txt

Scrape Jason and Terry's reviews given the list of restaurants:

    python findjatbar/scrape_jatbar_reviews.py < output/jatbar_restaurants.txt \
                                               > output/jatbar_reviews.json


## Step 2: scrape Yelp reviews

Yelp doesn't currently have a full API to retrieve reviews, so we must scrape them.

We need to first find out the corresponding Yelp URL for the each of the restaurants on Jatbar.
In order to do so, you must first register for
[Yelp's API](http://www.yelp.com/developers/getting_started).

    python findjatbar/find_corresponding_yelp_urls.py --consumer_key YOUR_CONSUMER_KEY \
                                                      --consumer_secret YOUR_CONSUMER_SECRET \
                                                      --token YOUR_TOKEN \
                                                      --token_secret YOUR_TOKEN_SECRET \
                                                      < output/jatbar_restaurants.txt \
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

    mkdir dataset_jason
    python findjatbar/split_data.py output/reviews.json Jason dataset_jason --seed 123

This creates the files `train.json`, `dev.json`, and `test.json`
in the specified `dataset_jason` directory.

Finally, we train a classifier using `train.json`, tune it on `dev.json`,
and test on `test.json`.
This step can eat up to about 5GB of memory.

    python findjatbar/classify.py dataset_jason --pr_curve output/pr_curve.png

## Step 4: scrape even more Yelp reviews and try to find Jason and Terry

We first try to find restaurants on Yelp that Jason and Terry might actually visit.
In this case, let's look restaurants (excluding the ones found on Jatbar)
within Santa Clara county that matches the query `burrito`:

    python findjatbar/search_yelp_restaurants.py --query burrito \
                                                 --locations locations.txt \
                                                 --exclude output/yelp_urls.txt \
                                                 --consumer_key YOUR_CONSUMER_KEY \
                                                 --consumer_secret YOUR_CONSUMER_SECRET \
                                                 --token YOUR_TOKEN \
                                                 --token_secret YOUR_TOKEN_SECRET \
                                                 > output/more_yelp_restraunts.txt

Next, we scrape the reviews from these restaurants:

    python findjatbar/scrape_more_yelp_reviews.py < output/more_yelp_restaurants.txt \
                                                  > output/more_yelp_reviews.json

## Acknowledgements

This project is heavily influenced by the following repository:

* word-salad: https://github.com/vchahun/word-salad

## License

Copyright (c) 2013, [Naoki Orii](http://www.cs.cmu.edu/~norii/)

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

- Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
- Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
