#!/usr/bin/env python

import os
import logging
import argparse
import json
from itertools import islice

import numpy as np
try:
    import cPickle as pickle
except:
    import pickle

import features

MASK = set(['desc', 'meta'])


def read_dataset(filename):
    X, y = [], []
    points = list(features.filter(features.extract(filename), MASK))
    for f, v in points:
        X.append(f.todict())
        y.append(v)
    return X, y


def main():
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    parser = argparse.ArgumentParser(description='Find Jason and Terry')
    parser.add_argument('--model', help='Pickled file tat contains best model', required=True)
    parser.add_argument('--test', help='Test json file', required=True)
    args = parser.parse_args()

    logging.info('Loading model...')
    with open(args.model, 'r') as f:
        d = pickle.load(f)
        vectorizer = d['vectorizer']
        model = d['model']

    logging.info('Loading reviews...')
    X, _ = read_dataset(args.test)
    X = vectorizer.transform(X)

    logging.info('Predicting')
    y = model.predict(X)

    def read_reviews(filename):
        with open(filename, 'r') as f:
            for line in f:
                review = json.loads(line.strip())['description']
                yield review
    reviews = list(read_reviews(args.test))
    positive_review_indices = np.where(y == 1)[0]

    for positive_review_index in positive_review_indices:
        print(reviews[positive_review_index].encode('utf8'))


if __name__ == '__main__':
    main()
