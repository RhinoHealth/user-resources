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
