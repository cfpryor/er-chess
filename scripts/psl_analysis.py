import json
import os
import sys
import pandas
import numpy

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_curve
from sklearn import metrics
from sklearn.metrics import auc
import matplotlib.pyplot as plt
from sklearn.utils.fixes import signature
from sklearn.metrics import f1_score

def run_analysis(infered_sorted_data, truth_sorted_data):
    truth_labels = []
    infered_labels = []
    for i in range(len(infered_sorted_data)):
        truth_labels.append(float(truth_sorted_data[i].strip().split('\t')[2]))
        infered_labels.append(float(infered_sorted_data[i].strip().split('\t')[2]))

    precision, recall, thresholds = precision_recall_curve(truth_labels, infered_labels)
    
    auc_val = auc(recall, precision)
    print(auc_val)
    
    step_kwargs = ({'step': 'post'} if 'step' in signature(plt.fill_between).parameters else {})
    plt.step(recall, precision, color='b', alpha=0.2,where='post')
    plt.fill_between(recall, precision, alpha=0.2, color='b', **step_kwargs)

    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.ylim([0.0, 1.05])
    plt.xlim([0.0, 1.0])
    plt.savefig('test_psl.png')
    
    threshold = 0.3
    thresholds = list(numpy.linspace(0,1,101))
    for thresh in thresholds:
        false_positive = 0
        false_negative = 0
        true_positive = 0
        true_negative = 0
        for i in range(len(infered_labels)):
            if infered_labels[i] < thresh:
                if truth_labels[i] == 0:
                    true_negative += 1
                else:
                    false_negative += 1
            else:
                if truth_labels[i] == 1:
                    true_positive += 1
                else:
                    false_positive += 1

        if true_positive + false_positive == 0:
            print(0)
        else:
            precision = true_positive / (true_positive + false_positive)
            recall = true_positive / (true_positive + false_negative)
            if (precision + recall) == 0:
                f1_mine = 0.0
            else:
                f1_mine = 2 * (precision * recall) / (precision + recall)
        print(f1_mine, precision, recall, thresh)
    false_positive = 0
    false_negative = 0
    true_positive = 0
    true_negative = 0
    for i in range(len(infered_labels)):
        if infered_labels[i] < threshold:
            if truth_labels[i] == 0:
                true_negative += 1
            else:
                false_negative += 1
        else:
            if truth_labels[i] == 1:
                true_positive += 1
            else:
                false_positive += 1
    
    if true_positive + false_positive == 0:
        print(0)
    else:
        precision = true_positive / (true_positive + false_positive)
        recall = true_positive / (true_positive + false_negative)
        f1_mine = 2 * (precision * recall) / (precision + recall)
    print(f1_mine, threshold)

def load_sorted_data(path):
    data = []
    with open(path, 'r') as file:
        for line in file:
            data.append(line)
    return sorted(data)

def _load_args(args):
    executable = args.pop(0)
    if (len(args) != 2 or ({'h', 'help'} & {arg.lower().strip().replace('-', '') for arg in args})):
        print("USAGE: python3 %s <infered values> <truth file>" % (executable), file = sys.stderr)
        sys.exit(1)

    infered_path = args.pop(0)
    truth_path = args.pop(0)

    return infered_path, truth_path

def main():
    infered_path, truth_path  = _load_args(sys.argv)
    infered_sorted_data = load_sorted_data(infered_path)
    truth_sorted_data = load_sorted_data(truth_path)

    run_analysis(infered_sorted_data, truth_sorted_data)
    #run_logistic_regression(train_examples, train_truth, test_examples, test_truth, data_path)

if (__name__ == '__main__'):
    main()
