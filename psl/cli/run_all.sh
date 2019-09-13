#!/bin/bash

python3 -W ignore ../../scripts/data_parsing/logistic_regression.py ../data/splits/split_0/
./run.sh > /dev/null 2>&1
python3 ../../scripts/psl_analysis.py inferred-predicates/SAMEUSER.txt ../data/splits/split_0/psl/same_user_truth.txt
sed -i 's/split_0/split_1/g' er-chess.data

python3 -W ignore ../../scripts/data_parsing/logistic_regression.py ../data/splits/split_1/
./run.sh > /dev/null 2>&1
python3 ../../scripts/psl_analysis.py inferred-predicates/SAMEUSER.txt ../data/splits/split_1/psl/same_user_truth.txt
sed -i 's/split_1/split_2/g' er-chess.data

python3 -W ignore ../../scripts/data_parsing/logistic_regression.py ../data/splits/split_2/
./run.sh > /dev/null 2>&1
python3 ../../scripts/psl_analysis.py inferred-predicates/SAMEUSER.txt ../data/splits/split_2/psl/same_user_truth.txt
sed -i 's/split_2/split_3/g' er-chess.data

python3 -W ignore ../../scripts/data_parsing/logistic_regression.py ../data/splits/split_3/
./run.sh > /dev/null 2>&1
python3 ../../scripts/psl_analysis.py inferred-predicates/SAMEUSER.txt ../data/splits/split_3/psl/same_user_truth.txt
sed -i 's/split_3/split_4/g' er-chess.data

python3 -W ignore ../../scripts/data_parsing/logistic_regression.py ../data/splits/split_4/
./run.sh > /dev/null 2>&1
python3 ../../scripts/psl_analysis.py inferred-predicates/SAMEUSER.txt ../data/splits/split_4/psl/same_user_truth.txt
sed -i 's/split_4/split_5/g' er-chess.data

python3 -W ignore ../../scripts/data_parsing/logistic_regression.py ../data/splits/split_5/
./run.sh > /dev/null 2>&1
python3 ../../scripts/psl_analysis.py inferred-predicates/SAMEUSER.txt ../data/splits/split_5/psl/same_user_truth.txt
sed -i 's/split_5/split_6/g' er-chess.data

python3 -W ignore ../../scripts/data_parsing/logistic_regression.py ../data/splits/split_6/
./run.sh > /dev/null 2>&1
python3 ../../scripts/psl_analysis.py inferred-predicates/SAMEUSER.txt ../data/splits/split_6/psl/same_user_truth.txt
sed -i 's/split_6/split_7/g' er-chess.data

python3 -W ignore ../../scripts/data_parsing/logistic_regression.py ../data/splits/split_7/
./run.sh > /dev/null 2>&1
python3 ../../scripts/psl_analysis.py inferred-predicates/SAMEUSER.txt ../data/splits/split_7/psl/same_user_truth.txt
sed -i 's/split_7/split_8/g' er-chess.data

python3 -W ignore ../../scripts/data_parsing/logistic_regression.py ../data/splits/split_8/
./run.sh > /dev/null 2>&1
python3 ../../scripts/psl_analysis.py inferred-predicates/SAMEUSER.txt ../data/splits/split_8/psl/same_user_truth.txt
sed -i 's/split_8/split_9/g' er-chess.data

python3 -W ignore ../../scripts/data_parsing/logistic_regression.py ../data/splits/split_9/
./run.sh > /dev/null 2>&1
python3 ../../scripts/psl_analysis.py inferred-predicates/SAMEUSER.txt ../data/splits/split_9/psl/same_user_truth.txt
sed -i 's/split_9/split_0/g' er-chess.data
