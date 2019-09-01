import json
import os
import re
import sys
import time


USERNAME_JW_FILENAME = 'username_jw_obs.txt'
USERNAME_L_FILENAME = 'username_l_obs.txt'
NAME_JW_FILENAME = 'name_jw_obs.txt'
NAME_L_FILENAME = 'name_l_obs.txt'
LOCATION_FILENAME = 'location_obs.txt'
COUNTRY_FILENAME = 'country_obs.txt'
OPPONENTS_FILENAME = 'opponents_obs.txt'
FRIENDS_FILENAME = 'friends_obs.txt'
WEBSITE_FILENAME = 'website_obs.txt'
RATING_B_FILENAME = 'ratings_b_obs.txt'
RATING_L_FILENAME = 'ratings_l_obs.txt'
RATING_R_FILENAME = 'ratings_r_obs.txt'
RATING_T_FILENAME = 'ratings_t_obs.txt'
STREAMER_FILENAME = 'streamer_obs.txt'
TITLE_FILENAME = 'title_obs.txt'
ECO_W_FILENAME = 'eco_w_obs.txt'
ECO_L_FILENAME = 'eco_l_obs.txt'
ECO_D_FILENAME = 'eco_d_obs.txt'
ECO_T_FILENAME = 'eco_t_obs.txt'


LR_LOCAL_FILENAME = 'lr_local_obs.txt'

SAMEUSER_TRUTH_FILENAME = 'same_user_truth.txt'
SAMEUSER_OBS_FILENAME = 'same_user_obs.txt'
SAMEUSER_TARGETS_FILENAME = 'same_user_target.txt'

TRAIN = 'train.json'
TEST = 'test.json'
RESULTS = 'lr_results.json'
PSL_DIR = 'psl'

HEADERS = ['users' ,'username_jw', 'username_l', 'name_jw', 'name_l', 'location', 'country', 'opponents', 'friends', 'same_website', 'ratings_b', 'ratings_l', 'ratings_r', 'rating_t', 'is_streamer', 'title', 'eco_w', 'eco_l', 'eco_d', 'eco_t','truth']

def load_data(train_data, test_data, lr_data, out_path):
    username_jw = []
    username_l = []
    name_jw = []
    name_l = []
    location = []
    country = []
    opponents = []
    friends = []
    website = []
    rating_b = []
    rating_l = []
    rating_r = []
    rating_t = []
    streamer = []
    title = []
    eco_w = []
    eco_l = []
    eco_d = []
    eco_t = []

    lr_local = []
    same_user_obs = []
    same_user_target = []
    same_user_truth = []

    for i in range(len(test_data)):
        test_example = test_data[i][0]
        print(test_example)
        name_i = test_example[0][0] + "_" + test_example[0][1]
        name_j = test_example[1][0] + "_" + test_example[1][1]

        if(name_i == name_j):
            print('TEST FILE DUPE: %s' % (name_i))
            continue

        username_jw.append([name_i, name_j, test_data[i][1]])
        username_jw.append([name_j, name_i, test_data[i][1]])

        username_l.append([name_i, name_j, test_data[i][2]])
        username_l.append([name_j, name_i, test_data[i][2]])

        name_jw.append([name_i, name_j, test_data[i][3]])
        name_jw.append([name_j, name_i, test_data[i][3]])

        name_l.append([name_i, name_j, test_data[i][4]])
        name_l.append([name_j, name_i, test_data[i][4]])

        location.append([name_i, name_j, test_data[i][5]])
        location.append([name_j, name_i, test_data[i][5]])

        country.append([name_i, name_j, test_data[i][6]])
        country.append([name_j, name_i, test_data[i][6]])

        opponents.append([name_i, name_j, test_data[i][7]])
        opponents.append([name_j, name_i, test_data[i][7]])

        friends.append([name_i, name_j, test_data[i][8]])
        friends.append([name_j, name_i, test_data[i][8]])

        website.append([name_i, name_j, test_data[i][9]])
        website.append([name_j, name_i, test_data[i][9]])

        rating_b.append([name_i, name_j, test_data[i][10]])
        rating_b.append([name_j, name_i, test_data[i][10]])

        rating_l.append([name_i, name_j, test_data[i][11]])
        rating_l.append([name_j, name_i, test_data[i][11]])

        rating_r.append([name_i, name_j, test_data[i][12]])
        rating_r.append([name_j, name_i, test_data[i][12]])

        rating_t.append([name_i, name_j, test_data[i][13]])
        rating_t.append([name_j, name_i, test_data[i][13]])

        streamer.append([name_i, name_j, test_data[i][14]])
        streamer.append([name_j, name_i, test_data[i][14]])

        title.append([name_i, name_j, test_data[i][15]])
        title.append([name_j, name_i, test_data[i][15]])

        eco_w.append([name_i, name_j, test_data[i][16]])
        eco_w.append([name_j, name_i, test_data[i][16]])

        eco_l.append([name_i, name_j, test_data[i][17]])
        eco_l.append([name_j, name_i, test_data[i][17]])

        eco_d.append([name_i, name_j, test_data[i][18]])
        eco_d.append([name_j, name_i, test_data[i][18]])

        eco_t.append([name_i, name_j, test_data[i][19]])
        eco_t.append([name_j, name_i, test_data[i][19]])

        lr_local.append([name_i, name_j, lr_data[i]])
        lr_local.append([name_j, name_i, lr_data[i]])

        same_user_target.append([name_i, name_j])
        same_user_target.append([name_j, name_i])

        same_user_truth.append([name_i, name_j, test_data[i][-1]])
        same_user_truth.append([name_j, name_i, test_data[i][-1]])

    for i in range(len(train_data)):
        train_example = train_data[i][0]
        name_i = train_example[0][0] + "_" + train_example[0][1]
        name_j = train_example[1][0] + "_" + train_example[1][1]
        
        if(name_i == name_j):
            print('TRAIN FILE DUPE: %s' % (name_i))
            continue

        username_jw.append([name_i, name_j, train_data[i][1]])
        username_jw.append([name_j, name_i, train_data[i][1]])

        username_l.append([name_i, name_j, train_data[i][2]])
        username_l.append([name_j, name_i, train_data[i][2]])

        name_jw.append([name_i, name_j, train_data[i][3]])
        name_jw.append([name_j, name_i, train_data[i][3]])

        name_l.append([name_i, name_j, train_data[i][4]])
        name_l.append([name_j, name_i, train_data[i][4]])

        location.append([name_i, name_j, train_data[i][5]])
        location.append([name_j, name_i, train_data[i][5]])

        country.append([name_i, name_j, train_data[i][6]])
        country.append([name_j, name_i, train_data[i][6]])

        opponents.append([name_i, name_j, train_data[i][7]])
        opponents.append([name_j, name_i, train_data[i][7]])

        friends.append([name_i, name_j, train_data[i][8]])
        friends.append([name_j, name_i, train_data[i][8]])

        website.append([name_i, name_j, train_data[i][9]])
        website.append([name_j, name_i, train_data[i][9]])

        rating_b.append([name_i, name_j, train_data[i][10]])
        rating_b.append([name_j, name_i, train_data[i][10]])

        rating_l.append([name_i, name_j, train_data[i][11]])
        rating_l.append([name_j, name_i, train_data[i][11]])

        rating_r.append([name_i, name_j, train_data[i][12]])
        rating_r.append([name_j, name_i, train_data[i][12]])

        rating_t.append([name_i, name_j, train_data[i][13]])
        rating_t.append([name_j, name_i, train_data[i][13]])

        streamer.append([name_i, name_j, train_data[i][14]])
        streamer.append([name_j, name_i, train_data[i][14]])

        title.append([name_i, name_j, train_data[i][15]])
        title.append([name_j, name_i, train_data[i][15]])

        eco_w.append([name_i, name_j, train_data[i][16]])
        eco_w.append([name_j, name_i, train_data[i][16]])

        eco_l.append([name_i, name_j, train_data[i][17]])
        eco_l.append([name_j, name_i, train_data[i][17]])

        eco_d.append([name_i, name_j, train_data[i][18]])
        eco_d.append([name_j, name_i, train_data[i][18]])

        eco_t.append([name_i, name_j, train_data[i][19]])
        eco_t.append([name_j, name_i, train_data[i][19]])

        same_user_obs.append([name_i, name_j, train_data[i][-1]])
        same_user_obs.append([name_j, name_i, train_data[i][-1]])
    
    with open(os.path.join(out_path, USERNAME_JW_FILENAME), 'w') as file:
        for sim in username_jw:
            file.write("\t".join([str(s) for s in sim]) + "\n")
    with open(os.path.join(out_path, USERNAME_L_FILENAME), 'w') as file:
        for sim in username_l:
            file.write("\t".join([str(s) for s in sim]) + "\n")
    with open(os.path.join(out_path, NAME_JW_FILENAME), 'w') as file:
        for sim in name_jw:
            file.write("\t".join([str(s) for s in sim]) + "\n")
    with open(os.path.join(out_path, NAME_L_FILENAME), 'w') as file:
        for sim in name_l:
            file.write("\t".join([str(s) for s in sim]) + "\n")
    with open(os.path.join(out_path, LOCATION_FILENAME), 'w') as file:
        for sim in location:
            file.write("\t".join([str(s) for s in sim]) + "\n")
    with open(os.path.join(out_path, COUNTRY_FILENAME), 'w') as file:
        for sim in country:
            file.write("\t".join([str(s) for s in sim]) + "\n")
    with open(os.path.join(out_path, OPPONENTS_FILENAME), 'w') as file:
        for sim in opponents:
            file.write("\t".join([str(s) for s in sim]) + "\n")
    with open(os.path.join(out_path, FRIENDS_FILENAME), 'w') as file:
        for sim in friends:
            file.write("\t".join([str(s) for s in sim]) + "\n")
    with open(os.path.join(out_path, WEBSITE_FILENAME), 'w') as file:
        for sim in website:
            file.write("\t".join([str(s) for s in sim]) + "\n")
    with open(os.path.join(out_path, RATING_B_FILENAME), 'w') as file:
        for sim in rating_b:
            file.write("\t".join([str(s) for s in sim]) + "\n")
    with open(os.path.join(out_path, RATING_L_FILENAME), 'w') as file:
        for sim in rating_l:
            file.write("\t".join([str(s) for s in sim]) + "\n")
    with open(os.path.join(out_path, RATING_R_FILENAME), 'w') as file:
        for sim in rating_r:
            file.write("\t".join([str(s) for s in sim]) + "\n")
    with open(os.path.join(out_path, RATING_T_FILENAME), 'w') as file:
        for sim in rating_t:
            file.write("\t".join([str(s) for s in sim]) + "\n")
    with open(os.path.join(out_path, STREAMER_FILENAME), 'w') as file:
        for sim in streamer:
            file.write("\t".join([str(s) for s in sim]) + "\n")
    with open(os.path.join(out_path, TITLE_FILENAME), 'w') as file:
        for sim in title:
            file.write("\t".join([str(s) for s in sim]) + "\n")
    with open(os.path.join(out_path, ECO_W_FILENAME), 'w') as file:
        for sim in eco_w:
            file.write("\t".join([str(s) for s in sim]) + "\n")
    with open(os.path.join(out_path, ECO_L_FILENAME), 'w') as file:
        for sim in eco_l:
            file.write("\t".join([str(s) for s in sim]) + "\n")
    with open(os.path.join(out_path, ECO_D_FILENAME), 'w') as file:
        for sim in eco_d:
            file.write("\t".join([str(s) for s in sim]) + "\n")
    with open(os.path.join(out_path, ECO_T_FILENAME), 'w') as file:
        for sim in eco_t:
            file.write("\t".join([str(s) for s in sim]) + "\n")

    with open(os.path.join(out_path, LR_LOCAL_FILENAME), 'w') as file:
        for lr_example in lr_local:
            file.write("\t".join([str(s) for s in lr_example]) + "\n")

    with open(os.path.join(out_path, SAMEUSER_OBS_FILENAME), 'w') as file:
        for same_user in same_user_obs:
            file.write("\t".join([str(s) for s in same_user]) + "\n")

    with open(os.path.join(out_path, SAMEUSER_TARGETS_FILENAME), 'w') as file:
        for same_user in same_user_target:
            file.write("\t".join([str(s) for s in same_user]) + "\n")

    with open(os.path.join(out_path, SAMEUSER_TRUTH_FILENAME), 'w') as file:
        for same_user in same_user_truth:
            file.write("\t".join([str(s) for s in same_user]) + "\n")

def load_users(user_path):
    with open(user_path, 'r') as file:
        return json.load(file)

def _load_args(args):
    executable = args.pop(0)
    if (len(args) != 1 or ({'h', 'help'} & {arg.lower().strip().replace('-', '') for arg in args})):
        print("USAGE: python3 %s <data path>" % (executable), file = sys.stderr)
        sys.exit(1)

    return args.pop(0)

def main():
    data_path = _load_args(sys.argv)
    if not os.path.isdir(os.path.join(data_path, PSL_DIR)):
        os.mkdir(os.path.join(data_path, PSL_DIR))
    
    train_data = load_users(os.path.join(data_path, TRAIN))
    test_data = load_users(os.path.join(data_path, TEST))
    lr_data = load_users(os.path.join(data_path, RESULTS))

    load_data(train_data, test_data, lr_data, os.path.join(data_path, PSL_DIR))

if (__name__ == '__main__'):
    main()
