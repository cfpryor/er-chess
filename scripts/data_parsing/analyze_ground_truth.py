import json
import os
import sys
import numpy
import pandas
import random

def print_entities(data):
    entities = {}
    ground_truth = []
    for row in data:
        if row[-1] == 1:
            ground_truth.append([row[0][0][0] + "_" + row[0][0][1], row[0][1][0] + "_" + row[0][1][1]])
    for user_i, user_j in ground_truth:
        if user_i not in entities:
            entities[user_i] = []
        if user_j not in entities:
            entities[user_j] = []
        entities[user_i].append(user_j)
        entities[user_j].append(user_i)
    for entity in entities:
        print(entity, entities[entity])
        
        
def load_data(path):
    with open(path, 'r') as file:
        return json.load(file)

def _load_args(args):
    executable = args.pop(0)
    if (len(args) != 1 or ({'h', 'help'} & {arg.lower().strip().replace('-', '') for arg in args})):
        print("USAGE: python3 %s <data path>" % (executable), file = sys.stderr)
        sys.exit(1)

    data_path = args.pop(0)

    return data_path

def main():
    data_path = _load_args(sys.argv)
    data = load_data(data_path)
    print_entities(data)

if (__name__ == '__main__'):
    main()
