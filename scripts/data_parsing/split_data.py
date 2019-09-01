import json
import os
import sys
import numpy
import pandas
import random

#HEADERS = ['users' ,'username_jw', 'username_l', 'name_jw', 'name_l', 'location', 'country', 'opponents', 'friends', 'same_website', 'ratings_b', 'ratings_l', 'ratings_r', 'rating_t', 'is_streamer', 'title', 'eco_w', 'eco_l', 'eco_d', 'eco_t', 'active', 'truth']
HEADERS = ['users' ,'username_jw', 'username_l', 'name_jw', 'name_l', 'location', 'country', 'opponents', 'friends', 'same_website', 'ratings_b', 'ratings_l', 'ratings_r', 'rating_t', 'is_streamer', 'title', 'eco_w', 'eco_l', 'eco_d', 'eco_t', 'truth']

SEED = 4
SPLIT_NUMBER = 10

SPLITS_PREFIX = 'split_'

TRAIN = 'train.json'
TEST = 'test.json'

def write_chunks(chunks, output_path):
    for i in range(len(chunks)):
        split_path = os.path.join(output_path, SPLITS_PREFIX + str(i))
        if not os.path.isdir(split_path):
            os.mkdir(split_path)

        train_path = os.path.join(split_path, TRAIN)
        test_path = os.path.join(split_path, TEST)

        with open(test_path, 'w') as file:
            json.dump(chunks[i], file, indent = 4)
        with open(train_path, 'w') as file:
            train_chunk = []
            for j in range(len(chunks)):
                if i == j:
                    continue
                train_chunk = train_chunk + chunks[j]
            json.dump(train_chunk, file, indent = 4)

def chunks(data, split_size):
    chunks = []
    for i in range(0, len(data), int(split_size)):
        if i + int(split_size) + SPLIT_NUMBER > len(data):
            chunks.append(data[i:])
            break
        chunks.append(data[i:i + int(split_size)])
    return(chunks)

def shuffle_data(data, seed_value = SEED):
    numpy.random.seed(seed_value)
    numpy.random.shuffle(data)
    return data

def count_positive(data):
    positive_count = 0
    for element in data:
        if element[-1] == 1:
            positive_count += 1
    return positive_count

def load_dataframe(data, headers = HEADERS):
    print("Starting Loading Dataframe")
    dataframe = pandas.DataFrame(data)
    dataframe.columns = headers
    return dataframe

def load_data(path):
    with open(path, 'r') as file:
        return json.load(file)

def _load_args(args):
    executable = args.pop(0)
    if (len(args) != 2 or ({'h', 'help'} & {arg.lower().strip().replace('-', '') for arg in args})):
        print("USAGE: python3 %s <data path> <output path>" % (executable), file = sys.stderr)
        sys.exit(1)

    data_path = args.pop(0)
    output_path = args.pop(0)

    return data_path, output_path

def main():
    data_path, output_path = _load_args(sys.argv)
    data = load_data(data_path)
    if not os.path.isdir(output_path):
        os.mkdir(output_path)
    shuffled_data = shuffle_data(data.copy())
    chunk_size = len(shuffled_data) / SPLIT_NUMBER
    chunks_list = chunks(shuffled_data, chunk_size)
    write_chunks(chunks_list, output_path)
    #dataframe_users = load_dataframe(data)
    #dataframe = dataframe_users.loc[:, dataframe_users.columns != 'Users']
    #truth = dataframe['Truth']
    #print(dataframe.loc[:, dataframe.columns != 'Truth'], truth)

if (__name__ == '__main__'):
    main()
