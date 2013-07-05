#!/usr/bin/env python

import json

import oauth2
import urllib
import requests


def search(query, location, consumer_key, consumer_secret, token, token_secret):
    host = 'api.yelp.com'
    path = '/v2/search'
    url_params = {
        'term': query,
        'location': location,
        'category_filter': 'restaurants',
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
    return response
