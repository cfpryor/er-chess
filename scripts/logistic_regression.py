import json
import os
import sys
import pandas

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_curve
from sklearn import metrics
from sklearn.metrics import auc
import matplotlib.pyplot as plt
from sklearn.utils.fixes import signature
from sklearn.metrics import f1_score

HEADERS = ['Users', 'Username', 'Full_Name', 'Country', 'Followers', 'Bullet_Current', 'Blitz_Current', 'Rapid_Current', 'Tactics_Current', 'FIDE', 'USCF', 'Truth']

TRAIN = 'train.json'
TEST = 'test.json'
RESULTS = 'lr_results.json'

def run_logistic_regression(train_data, train_labels, test_data, test_labels, data_path):
    logisticRegr = LogisticRegression()
    logisticRegr.fit(train_data, train_labels)
    prediction_probs = logisticRegr.predict_proba(test_data)
    precision, recall, thresholds = precision_recall_curve(test_labels, prediction_probs.transpose()[1].transpose())

    with open(os.path.join(data_path, RESULTS), 'w') as file:
        json.dump(list(prediction_probs.transpose()[1]), file, indent = 4)

    auc_val = auc(recall, precision)
    print(auc_val)

    step_kwargs = ({'step': 'post'} if 'step' in signature(plt.fill_between).parameters else {})
    plt.step(recall, precision, color='b', alpha=0.2,where='post')
    plt.fill_between(recall, precision, alpha=0.2, color='b', **step_kwargs)

    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.ylim([0.0, 1.05])
    plt.xlim([0.0, 1.0])
    plt.savefig('test.png')
    
    logisticRegr = LogisticRegression()
    logisticRegr.fit(train_data, train_labels)
    predictions = logisticRegr.predict(test_data)
    
    threshold = 0.5
    
    false_positive = 0
    false_negative = 0
    true_positive = 0
    true_negative = 0
    for i in range(len(predictions)):
        if predictions[i] < threshold:
            if test_labels[i] == 0:
                true_negative += 1
            else:
                false_negative += 1
        else:
            if test_labels[i] == 1:
                true_positive += 1
            else:
                false_positive += 1
    
    precision = true_positive / (true_positive + false_positive)
    recall = true_positive / (true_positive + false_negative)
    f1_mine = 2 * (precision * recall) / (precision + recall)
    print(f1_mine)

    #f1 = f1_score(test_labels, predictions)
    #print(f1, f1_mine)

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
    if (len(args) != 1 or ({'h', 'help'} & {arg.lower().strip().replace('-', '') for arg in args})):
        print("USAGE: python3 %s <data path>" % (executable), file = sys.stderr)
        sys.exit(1)

    return args.pop(0)

def main():
    data_path = _load_args(sys.argv)
    
    train_data = load_data(os.path.join(data_path, TRAIN))
    train_dataframe_users = load_dataframe(train_data)
    train_dataframe = train_dataframe_users.loc[:, train_dataframe_users.columns != 'Users']
    train_examples = train_dataframe.loc[:, train_dataframe.columns != 'Truth']
    train_truth = train_dataframe['Truth']

    test_data = load_data(os.path.join(data_path, TEST))
    test_dataframe_users = load_dataframe(train_data)
    test_dataframe = test_dataframe_users.loc[:, test_dataframe_users.columns != 'Users']
    test_examples = test_dataframe.loc[:, test_dataframe.columns != 'Truth']
    test_truth = test_dataframe['Truth']
    
    run_logistic_regression(train_examples, train_truth, test_examples, test_truth, data_path)

if (__name__ == '__main__'):
    main()
