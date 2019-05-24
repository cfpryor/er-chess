import json
import os
import re
import sys
import time

USERNAME_SIM_FILENAME = 'username_sim_obs.txt'
NAME_SIM_FILENAME = 'name_sim_obs.txt'
COUNTRY_SAME_FILENAME = 'country_same_obs.txt'
LR_LOCAL_FILENAME = 'lr_local_obs.txt'
WEBSITE_USERNAME_FILENAME = 'web_user_obs.txt'

SIMILAR_PROFILE_FILENAME = 'profile_sim.txt'

SAMEUSER_TRUTH_FILENAME = 'same_user_truth.txt'
SAMEUSER_OBS_FILENAME = 'same_user_obs.txt'
SAMEUSER_TARGETS_FILENAME = 'same_user_target.txt'

TRAIN = 'train.json'
TEST = 'test.json'
RESULTS = 'lr_results.json'
PSL_DIR = 'psl'

def load_data(train_data, test_data, lr_data, out_path):
    username_sim = []
    name_sim = []
    country_same = []
    lr_local = []
    same_user_obs = []
    same_user_target = []
    same_user_truth = []
    profile_sim = []
    web_user = []

    for i in range(len(test_data)):
        test_example = test_data[i][0]
        name_i = test_example[0][0] + "_" + test_example[0][1]
        name_j = test_example[1][0] + "_" + test_example[1][1]

        username_sim.append([name_i, name_j, test_data[i][1]])
        username_sim.append([name_j, name_i, test_data[i][1]])
        
        name_sim.append([name_i, name_j, test_data[i][2]])
        name_sim.append([name_j, name_i, test_data[i][2]])
        
        country_same.append([name_i, name_j, test_data[i][3]])
        country_same.append([name_j, name_i, test_data[i][3]])
    
        lr_local.append([name_i, name_j, lr_data[i] ** 2])
        lr_local.append([name_j, name_i, lr_data[i] ** 2])
        
        same_user_target.append([name_i, name_j])
        same_user_target.append([name_j, name_i])
        
        same_user_truth.append([name_i, name_j, test_data[i][-1]])
        same_user_truth.append([name_j, name_i, test_data[i][-1]])
        
        profile_sim.append([name_i, name_j])
        profile_sim.append([name_j, name_i])

        if test_data[i][1] > 0.95 and test_example[0][1] != test_example[1][1]:
            web_user.append([name_i, name_j, 1.0])

    for i in range(len(train_data)):
        train_example = train_data[i][0]
        name_i = train_example[0][0] + "_" + train_example[0][1]
        name_j = train_example[1][0] + "_" + train_example[1][1]

        username_sim.append([name_i, name_j, train_data[i][1]])
        username_sim.append([name_j, name_i, train_data[i][1]])
        
        name_sim.append([name_i, name_j, train_data[i][2]])
        name_sim.append([name_j, name_i, train_data[i][2]])
        
        country_same.append([name_i, name_j, train_data[i][3]])
        country_same.append([name_j, name_i, train_data[i][3]])
        
        same_user_obs.append([name_i, name_j, train_data[i][-1]])
        same_user_obs.append([name_j, name_i, train_data[i][-1]])

        profile_sim.append([name_i, name_j])
        profile_sim.append([name_j, name_i])
        
        if train_data[i][1] > 0.95 and train_example[0][1] != train_example[1][1]:
            web_user.append([name_i, name_j, 1.0])

    with open(os.path.join(out_path, USERNAME_SIM_FILENAME), 'w') as file:
        for sim in username_sim:
            file.write("\t".join([str(s) for s in sim]) + "\n")
    
    with open(os.path.join(out_path, NAME_SIM_FILENAME), 'w') as file:
        for sim in name_sim:
            file.write("\t".join([str(s) for s in sim]) + "\n")
    
    with open(os.path.join(out_path, COUNTRY_SAME_FILENAME), 'w') as file:
        for same in country_same:
            file.write("\t".join([str(s) for s in same]) + "\n")
    
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
    
    with open(os.path.join(out_path, SIMILAR_PROFILE_FILENAME), 'w') as file:
        for sim_profile in profile_sim:
            file.write("\t".join([str(s) for s in sim_profile]) + "\n")
    
    with open(os.path.join(out_path, WEBSITE_USERNAME_FILENAME), 'w') as file:
        for i in web_user: 
            file.write("\t".join([str(s) for s in i]) + "\n")

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
