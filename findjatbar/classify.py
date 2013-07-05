#!/usr/bin/env python

import os
import logging
import argparse

from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score

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

    parser = argparse.ArgumentParser(description='Run classification')
    parser.add_argument('prefix', help='directory which contains '
                                       '{jatbar_reviews,yelp_reviews}.txt')
    args = parser.parse_args()

    vectorizer = DictVectorizer()

    logging.info('Loading training data...')
    X_train, y_train = read_dataset(os.path.join(args.prefix, 'train.json'))
    X_train = vectorizer.fit_transform(X_train)

    logging.info('Loading development data...')
    X_dev, y_dev = read_dataset(os.path.join(args.prefix, 'dev.json'))
    X_dev = vectorizer.transform(X_dev)

    logging.info('Training...')
    f1_scores = []
    for regularization in (100, 10, 1, 0.1, 0.01):
        model = LogisticRegression(penalty='l1', C=regularization)
        logging.info('regularization: {0}'.format(regularization))
        model.fit(X_train, y_train)
        score = f1_score(y_dev, model.predict(X_dev))
        f1_scores.append((score, regularization, model))
        logging.info('Dev f1: {0}'.format(f1_score))

    best_f1_score, best_regularization, best_model = max(f1_scores)

    print('Loading test data...')
    X_test, y_test = read_dataset(os.path.join(args.prefix, 'test.json'))
    X_test = vectorizer.transform(X_test)

    print('Tuned regularization: {} (f1={})'.format(best_regularization, best_f1_score))
    print('Test f1: {0}'.format(f1_score(y_test, best_model.predict(X_test))))

if __name__ == '__main__':
    main()
