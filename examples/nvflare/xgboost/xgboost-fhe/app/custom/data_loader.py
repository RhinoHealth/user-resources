from pathlib import Path

import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split

from nvflare.app_opt.xgboost.data_loader import XGBDataLoader

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


def prep_df(df):
    numeric = df[NUMERIC_COLS].astype("float")
    categorical = df[CATEGORICAL_COLS].astype("category")
    labels = df[LABEL_COL].astype("int")
    dmat = xgb.DMatrix(
        pd.concat([numeric, categorical], axis=1),
        label=labels,
        enable_categorical=True,
    )
    return dmat


class DataLoader(XGBDataLoader):
    def __init__(self):
        data_dirs = [
            x for x in Path("/input/datasets/").iterdir() if x.resolve().is_dir()
        ]
        self.data_path = Path(data_dirs[0] / "dataset.csv")

    def load_data(self):
        df = pd.read_csv(self.data_path)
        df_train, df_valid = train_test_split(
            df, test_size=0.25, random_state=42, stratify=df[LABEL_COL].values
        )

        dmat_train = prep_df(df_train)
        dmat_valid = prep_df(df_valid)

        return dmat_train, dmat_valid
