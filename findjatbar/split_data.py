#!/usr/bin/env python

import os
import argparse
import random
import json


def load_data(filename):
    with open(filename, 'r') as f:
        for line in f:
            yield json.loads(line.strip())


def main():
    parser = argparse.ArgumentParser(description='Split data into train, dev, and test')
    parser.add_argument('json', help='Input data file')
    parser.add_argument('target', help='Who should we consider as positive',
                        choices=('Jason', 'Terry', 'Both'))
    parser.add_argument('output_dir')
    parser.add_argument('--seed', type=int, default=0)
    args = parser.parse_args()

    random.seed(args.seed)

    data = list(load_data(args.json))

    if args.target == 'Jason' or args.target == 'Terry':
        pos_data = filter(lambda d: d['author'] == args.target, data)
    elif args.target == 'Both':
        pos_data = filter(lambda d: d['author'] == 'Jason' or
                                    d['author'] == 'Terry', data)
    neg_data = filter(lambda d: d['author'] != 'Jason' and
                                d['author'] != 'Terry', data)

    for d in pos_data:
        d['label'] = 1
    for d in neg_data:
        d['label'] = 0

    random.shuffle(pos_data)
    random.shuffle(neg_data)

    train_ratio = 0.7
    dev_ratio = 0.2
    assert(train_ratio + dev_ratio < 1)

    pos_num_data = len(pos_data)
    neg_num_data = len(neg_data)

    pos_split1 = int(pos_num_data * train_ratio)
    pos_split2 = int(pos_num_data * (train_ratio + dev_ratio))
    neg_split1 = int(neg_num_data * train_ratio)
    neg_split2 = int(neg_num_data * (train_ratio + dev_ratio))

    train_data = pos_data[:pos_split1] + neg_data[:neg_split1]
    dev_data = pos_data[pos_split1:pos_split2] + neg_data[neg_split1:neg_split2]
    test_data = pos_data[pos_split2:] + neg_data[neg_split2:]

    def write_file(filename, data):
        with open(filename, 'w') as f:
            for d in data:
                f.write('{}\n'.format(json.dumps(d)))

    write_file(os.path.join(args.output_dir, 'train.json'), train_data)
    write_file(os.path.join(args.output_dir, 'dev.json'), dev_data)
    write_file(os.path.join(args.output_dir, 'test.json'), test_data)


if __name__ == '__main__':
    main()
