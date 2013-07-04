#!/usr/bin/env python

import sys
import argparse
import time
import re
import logging
import json

import lxml.html
import requests

from reviews import Review


def scrape(url, restaurant_id):
    url = 'http://www.yelp.com/biz/99-chicken-santa-clara'
    res = requests.get(url)
    doc = lxml.html.fromstring(res.content)

    reviews = []
    for li in doc.findall(".//div[@id='reviews-other']/ul/li"):
        comment_node = li.find(".//p[@itemprop='description']")
        entry = ' '.join(comment_node.itertext())
        entry = entry.replace('\n', ' ')
        entry = entry.strip()

        a_node = li.find(".//li[@class='user-name']/a")
        author = ''
        if a_node is not None:
            href = a_node.values()[0]
            # href = "/user_details?userid=BZtafoOqXIxTvUgkoEpBJw"
            author = href[href.find('=') + 1:]

        review = Review(author=author, restaurant_id=restaurant_id,
                        entry=entry)
        reviews.append(review)
    return reviews


def main():
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    # Don't log messages for `requests` unless they are at least warnings
    requests_log = logging.getLogger("requests")
    requests_log.setLevel(logging.WARNING)

    for i, line in enumerate(sys.stdin):
        # logging.info('Restaurant {}'.format(i))

        columns = line.strip().split()
        if len(columns) < 2:
            continue
        restaurant_id, yelp_url = columns
        reviews = scrape(yelp_url, restaurant_id)
        for review in reviews:
            print('{}'.format(json.dumps({'restaurant_id': review.restaurant_id,
                                          'author': review.author,
                                          'description': review.entry.encode('utf8')})))
        time.sleep(1)

if __name__ == '__main__':
    main()
