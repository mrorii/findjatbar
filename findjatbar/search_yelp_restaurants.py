#!/usr/bin/env python

import sys
import argparse
import logging
from collections import namedtuple

import yelp_api

Restaurant = namedtuple('Restaurant', 'url, review_count')

def get_yelp_restaurants(location, args):
    response = yelp_api.search(query=args.query,
                               location=location,
                               consumer_key=args.consumer_key,
                               consumer_secret=args.consumer_secret,
                               token=args.token,
                               token_secret=args.token_secret)
    if 'businesses' in response and response['businesses']:
        return map(lambda business: Restaurant(url=business['url'],
                                               review_count=business['review_count']),
                                    response['businesses'])

def main():
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    # Don't log messages for `requests` unless they are at least warnings
    requests_log = logging.getLogger("requests")
    requests_log.setLevel(logging.WARNING)

    parser = argparse.ArgumentParser(description='Search Yelp restaurants by query')
    parser.add_argument('--consumer_key', help='OAuth consumer key', required=True)
    parser.add_argument('--consumer_secret', help='OAuth consumer secret', required=True)
    parser.add_argument('--token', help='OAuth token', required=True)
    parser.add_argument('--token_secret', help='OAuth token secret', required=True)
    parser.add_argument('--query', help='Search query', required=True)
    parser.add_argument('--locations', help='Locations to search on', required=True)
    parser.add_argument('--exclude', help='Restaurants to exclude', required=True)
    args = parser.parse_args()

    def load_exclude_restaurants(filename):
        with open(filename, 'r') as f:
            for line in f:
                columns = line.strip().split('\t')
                if len(columns) == 2:
                    yield columns[1]

    exclude_restaurants = set(load_exclude_restaurants(args.exclude))

    yelp_restaurants = []
    locations = map(lambda line: line.strip(), open(args.locations).readlines())
    for location in locations:
        restaurants = get_yelp_restaurants(location, args)
        if restaurants:
            yelp_restaurants.extend(restaurants)

    valid_restaurants = filter(lambda restaurant: restaurant.url not in
                                                  exclude_restaurants, yelp_restaurants)
    for restaurant in set(valid_restaurants):
        print('{}\t{}'.format(restaurant.url, restaurant.review_count))

if __name__ == '__main__':
    main()
