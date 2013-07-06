#!/usr/bin/env python

import json

import lxml.html
import oauth2
import urllib
import requests

from reviews import Review


def scrape(url, restaurant_id):
    res = requests.get(url)
    doc = lxml.html.fromstring(res.content)

    for li in doc.findall(".//div[@id='reviews-other']/ul/li"):
        comment_node = li.find(".//p[@itemprop='description']")
        if comment_node is None:
            continue
        entry = ' '.join(comment_node.itertext())
        entry = entry.replace('\n', ' ')
        entry = entry.strip()

        a_node = li.find(".//li[@class='user-name']/a")
        author = ''
        if a_node is not None:
            href = a_node.values()[0]
            # `href` will look like "/user_details?userid=BZtafoOqXIxTvUgkoEpBJw"
            author = href[href.find('=') + 1:]

        review = Review(author=author, restaurant_id=restaurant_id, entry=entry)
        yield review


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
