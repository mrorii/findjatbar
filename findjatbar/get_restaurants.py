#!/usr/bin/env python

import argparse
from itertools import islice

import lxml.html
import requests


def main():
    parser = argparse.ArgumentParser(description='Get list of '
                                                 'Jatbar restaurants')
    parser.add_argument('--archive_time', help='archive time',
                        default=20090523085018)
    args = parser.parse_args()

    web_archive_url = 'http://web.archive.org/web'
    jatbar_url = 'http://www.jatbar.com/'
    url = '{}/{}/{}'.format(web_archive_url, args.archive_time, jatbar_url)
    res = requests.get(url)
    doc = lxml.html.fromstring(res.content)
    xpath = ".//select[@name='restaurants']/option"

    for i, restaurant in enumerate(islice(doc.findall(xpath), 1, None)):
        # Skip the first option as it is not a restaurant
        restaurant_name = restaurant.text.strip()
        restaurant_url = restaurant.values()[0]
        print('{}\t{}\t{}'.format(i + 1, restaurant_name, restaurant_url))

if __name__ == '__main__':
    main()
