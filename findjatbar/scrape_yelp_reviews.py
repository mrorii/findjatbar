#!/usr/bin/env python

import sys
import time
import re
import logging
import json

import yelp_helper


def main():
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    # Don't log messages for `requests` unless they are at least warnings
    requests_log = logging.getLogger("requests")
    requests_log.setLevel(logging.WARNING)

    for i, line in enumerate(sys.stdin):
        columns = line.strip().split()
        if len(columns) < 2:
            continue
        restaurant_id, yelp_url = columns
        reviews = yelp_helper.scrape(yelp_url, restaurant_id)
        for review in reviews:
            print('{}'.format(json.dumps({'restaurant_id': review.restaurant_id,
                                          'author': review.author,
                                          'description': review.entry.encode('utf8')})))
        time.sleep(1)

if __name__ == '__main__':
    main()
