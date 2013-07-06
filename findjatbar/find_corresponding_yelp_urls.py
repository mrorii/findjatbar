#!/usr/bin/env python

import sys
import re
import argparse
import logging

import yelp_api

def get_location(jatbar_url):
    search = re.search(r'http://www.jatbar.com/reviews/(.*)/.*.asp',
                       jatbar_url,
                       re.IGNORECASE)
    if search:
        location = search.group(1)
        location = location.replace('_', ' ')
        location = '%s, CA' % location  # Jatbar's URL only contains city names
        return location
    else:
        raise RuntimeError("Location not found for: {}".format(jatbar_url))


def get_yelp_url(restaurant_name, location,
                 consumer_key, consumer_secret, token, token_secret):
    response = yelp_api.search(query=restaurant_name,
                               location=location,
                               consumer_key=consumer_key,
                               consumer_secret=consumer_secret,
                               token=token,
                               token_secret=token_secret)

    # We assume that the 1st search result will be
    # the corresponding restaurant on Yelp
    if 'businesses' in response and response['businesses']:
        return response['businesses'][0]['url']
    else:
        return ''


def main():
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    # Don't log messages for `requests` unless they are at least warnings
    requests_log = logging.getLogger("requests")
    requests_log.setLevel(logging.WARNING)

    parser = argparse.ArgumentParser(description='Find corresponding '
                                                 'Yelp URLs')
    parser.add_argument('--consumer_key', help='OAuth consumer key',
                        required=True)
    parser.add_argument('--consumer_secret', help='OAuth consumer secret',
                        required=True)
    parser.add_argument('--token', help='OAuth token', required=True)
    parser.add_argument('--token_secret', help='OAuth token secret',
                        required=True)
    args = parser.parse_args()

    for i, line in enumerate(sys.stdin):
        restaurant_id, restaurant_name, jatbar_url = line.strip().split('\t')
        restaurant_name = re.sub(r'\(Closed\)', '', restaurant_name)
        location = get_location(jatbar_url)
        yelp_url = get_yelp_url(restaurant_name,
                                location,
                                consumer_key=args.consumer_key,
                                consumer_secret=args.consumer_secret,
                                token=args.token,
                                token_secret=args.token_secret)
        print('{}\t{}'.format(restaurant_id, yelp_url))

if __name__ == '__main__':
    main()
