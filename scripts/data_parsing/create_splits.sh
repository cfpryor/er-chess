#!/bin/bash
trap exit SIGINT

# Main
function main() {
python3 create_feature_vector.py ../../data/finalized_dataset/finalized_data.json ../../data/positive_ground_truth.json
python3 split_data.py features.txt splits
python3 logistic_regression.py splits/split_1/
python3 logistic_regression.py splits/split_0
python3 logistic_regression.py splits/split_2
python3 logistic_regression.py splits/split_3
python3 logistic_regression.py splits/split_4
python3 logistic_regression.py splits/split_5
python3 logistic_regression.py splits/split_6
python3 logistic_regression.py splits/split_7
python3 logistic_regression.py splits/split_8
python3 logistic_regression.py splits/split_9

python3 prepare_psl_data.py splits/split_0
python3 prepare_psl_data.py splits/split_1
python3 prepare_psl_data.py splits/split_2
python3 prepare_psl_data.py splits/split_3
python3 prepare_psl_data.py splits/split_4
python3 prepare_psl_data.py splits/split_5
python3 prepare_psl_data.py splits/split_6
python3 prepare_psl_data.py splits/split_7
python3 prepare_psl_data.py splits/split_8
python3 prepare_psl_data.py splits/split_9
}
main "$@"
