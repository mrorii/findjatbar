#!/usr/bin/env python

from collections import deque, Counter
import re
import json

_stop = set(['and', 'n\'', 'or', 'with', 'w', 'without']
            + ['a', 'the', 'of', 'in', 'on']
            + ['de', 'di', 'o', 'con', 'a', 'la', 'al', 'alla', 's', 'ai', 'e', 'et', 'y']
            + ['l', 'lb', 'oz', 'pt', 'qt', 'pint', 'quart', 'pack', 'pc', 'pcs', 'half']
            + ['lg', 'sm', 'med', 'large', 'small', 'medium'])

wRE = re.compile('[^a-zA-Z\']')
spRE = re.compile('\s+')


class FeatureVector(dict):
    def todict(self):
        def kv():
            for fname, fval in self.iteritems():
                yield ':'.join(fname), fval
        return dict(kv())


def tokenize(name):
    name = wRE.sub(' ', name)
    name = spRE.sub(' ', name).strip()
    name = name.lower()
    return name.split()


def ngrams(tokens):
    """ N-gram features """
    ngram = deque(maxlen=3)
    for token in tokens:
        ngram.append(token)
        yield (1, token)
        if len(ngram) >= 2:
            yield (2, '%s %s' % (ngram[-2], ngram[-1]))
        if len(ngram) == 3:
            yield (3, ' '.join(ngram))


def description(item):
    desc = tokenize(item['description'])
    if not desc:
        yield ('desc', '?')
    else:
        for (c, w) in ngrams(desc):
            yield ('desc', str(c), w)


def extract(filename):
    with open(filename) as f:
        for line in f:
            review = json.loads(line)
            features = FeatureVector()
            for feat in description(review):
                features[feat] = 1
            label = review['label'] if 'label' in review else -1
            yield features, label


def filter(stream, mask):
    for features, label in stream:
        features = FeatureVector((k, v) for k, v in features.iteritems() if k[0] in mask)
        yield features, label


def prune(instances, threshold=5):
    feature_counts = Counter()
    for instance in instances:
        for feature in instance:
            feature_counts[feature] += 1

    valid_features = set(f for f in feature_counts if feature_counts[f] >= threshold)

    for instance in instances:
        for feature in instance.keys():
            if not feature in valid_features:
                del instance[feature]
    return instances
