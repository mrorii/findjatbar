#!/usr/bin/env python

import sys
import math
import logging
import time
import json

import yelp_helper


def main():
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    # Don't log messages for `requests` unless they are at least warnings
    requests_log = logging.getLogger("requests")
    requests_log.setLevel(logging.WARNING)

    PER_PAGE = 40

    for i, line in enumerate(sys.stdin):
        yelp_url, review_count = line.strip().split()
        num_pages = int(math.ceil(float(review_count) / PER_PAGE))

        for page in xrange(num_pages):
            url = '{}?start={}'.format(yelp_url, page * PER_PAGE)
            reviews = yelp_helper.scrape(url, restaurant_id=0)
            for review in reviews:
                print('{}'.format(json.dumps({'restaurant_id': review.restaurant_id,
                                              'author': review.author,
                                              'description': review.entry.encode('utf8')})))
        time.sleep(1)

if __name__ == '__main__':
    main()
