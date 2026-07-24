from pathlib import Path

# Change to Rhino filepaths
data_dirs = [x for x in Path("/input/datasets/").iterdir() if x.resolve().is_dir()]
TRAIN_DATA_PATH = Path(data_dirs[0] / "dataset.csv")
TEST_DATA_PATH = "/input/dataset.csv"
PREDICTION_PATH = "/output/dataset.csv"

# Data attributes
LABEL_COL = "loan_status"
CATEGORICAL_COLS = [
    "person_home_ownership",
    "loan_intent",
    "loan_grade",
    "cb_person_default_on_file",
]
NUMERIC_COLS = [
    "person_age",
    "person_income",
    "person_emp_length",
    "loan_amnt",
    "loan_int_rate",
    "cb_person_cred_hist_length",
]

# Training params
NUM_ROUNDS = 1  # 1 round of boosting per round of federation
