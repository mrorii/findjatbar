#!/usr/bin/env python

import os
import logging
import argparse
from itertools import islice

from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_recall_curve, auc
import pylab as pl

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
                                       '{train,dev,test}.json')
    parser.add_argument('--pr_curve', help='File to save precision-recall curve')
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
    for regularization in (0.01, 0.1, 1, 10, 100, 1000):
        model = LogisticRegression(penalty='l1', C=regularization, class_weight='auto')
        logging.info('regularization parameter: {0}'.format(regularization))
        model.fit(X_train, y_train)
        score = f1_score(y_dev, model.predict(X_dev))
        f1_scores.append((score, regularization, model))
        logging.info('Dev f1: {0}'.format(score))

    best_f1_score, best_regularization, best_model = max(f1_scores)

    logging.info('Loading test data...')
    X_test, y_test = read_dataset(os.path.join(args.prefix, 'test.json'))
    X_test = vectorizer.transform(X_test)

    print('Tuned regularization parameter: {0} (f1={1})'.format(best_regularization, best_f1_score))
    print('Test f1: {0}'.format(f1_score(y_test, best_model.predict(X_test))))

    weights = vectorizer.inverse_transform(best_model.coef_)[0]
    sorted_weights = sorted(weights.iteritems(), key=lambda x: x[1], reverse=True)
    print
    print('Top 30 weights:')
    for i, (feat, weight) in enumerate(islice(sorted_weights, 30)):
        print('{0}: {1} {2}'.format(i+1, feat, weight))

    print
    print('Bottom 30 weights:')
    for i, (feat, weight) in enumerate(islice(reversed(sorted_weights), 30)):
        print('{0} {1} {2}'.format(i+1, feat, weight))

    probas_ = best_model.predict_proba(X_test)
    precision, recall, thresholds = precision_recall_curve(y_test, probas_[:, 1])
    area = auc(recall, precision)

    if args.pr_curve:
        pl.clf()
        pl.plot(recall, precision, label='Precision-Recall curve')
        pl.xlabel('Recall')
        pl.ylabel('Precision')
        pl.ylim([0.0, 1.05])
        pl.xlim([0.0, 1.0])
        pl.title('Precision-Recall example: AUC=%0.2f' % area)
        pl.legend(loc="lower left")
        pl.savefig(args.pr_curve)

if __name__ == '__main__':
    main()
