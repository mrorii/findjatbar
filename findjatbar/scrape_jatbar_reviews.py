#!/usr/bin/env python

import sys
import argparse
import time
import json

import lxml.html
import requests

from reviews import Review

AUTHORS = ['Jason', 'Terry']


def scrape(url, restaurant_id):
    res = requests.get(url)
    doc = lxml.html.fromstring(res.content)

    for AUTHOR in AUTHORS:
        xpath = ".//a[@name='{}']".format(AUTHOR)
        node = doc.find(xpath)
        if node is None:
            continue
        review_node = node.getparent().getnext()
        if review_node is None:
            continue
        entry = ' '.join(review_node.itertext())
        entry = entry.replace('\n', ' ')
        entry = entry.strip()

        review = Review(author=AUTHOR, restaurant_id=restaurant_id, entry=entry)
        yield review


def main():
    parser = argparse.ArgumentParser(description='Get list of Jatbar restaurants')
    parser.add_argument('--archive_time', help='archive time', default=20090523085018)
    args = parser.parse_args()

    WEB_ARCHIVE_URL = 'http://web.archive.org/web'

    for line in sys.stdin:
        restaurant_id, restaurant_name, jatbar_url = line.strip().split('\t')
        url = '{}/{}/{}'.format(WEB_ARCHIVE_URL, args.archive_time, jatbar_url)
        reviews = scrape(url, restaurant_id)
        for review in reviews:
            print('{}'.format(json.dumps({'restaurant_id': review.restaurant_id,
                                          'author': review.author,
                                          'description': review.entry.encode('utf8')})))
        time.sleep(1)

if __name__ == '__main__':
    main()
