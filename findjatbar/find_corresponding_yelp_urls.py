#!/usr/bin/env python

import sys
import re
import argparse
import logging

import json
import oauth2
import urllib
import requests


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
    host = 'api.yelp.com'
    path = '/v2/search'
    url_params = {
        'term': restaurant_name,
        'location': location,
    }
    encoded_params = urllib.urlencode(url_params)

    url = 'http://%s%s?%s' % (host, path, encoded_params)
    consumer = oauth2.Consumer(consumer_key, consumer_secret)
    oauth_request = oauth2.Request('GET', url, {})

    oauth_request.update({'oauth_nonce': oauth2.generate_nonce(),
                          'oauth_timestamp': oauth2.generate_timestamp(),
                          'oauth_token': token,
                          'oauth_consumer_key': consumer_key})
    token = oauth2.Token(token, token_secret)
    oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer,
                               token)
    signed_url = oauth_request.to_url()

    res = requests.get(signed_url)
    response = json.loads(res.content)

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
        if i % 100 == 0:
            logging.info('Restaurant {}'.format(i))
        print('{}\t{}'.format(restaurant_id, yelp_url))

if __name__ == '__main__':
    main()
