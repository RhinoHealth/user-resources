#!/usr/bin/env python
import sys

import pandas as pd
import xgboost as xgb

from fl_config import (
    TEST_DATA_PATH,
    PREDICTION_PATH,
    NUMERIC_COLS,
    CATEGORICAL_COLS,
    LABEL_COL,
)

if __name__ == "__main__":
    model_path = sys.argv[1]

    df_test = pd.read_csv(TEST_DATA_PATH)
    numeric = df_test[NUMERIC_COLS].astype("float")
    categorical = df_test[CATEGORICAL_COLS].astype("category")
    labels = df_test[LABEL_COL].astype("int")
    dtest = xgb.DMatrix(
        pd.concat([numeric, categorical], axis=1), enable_categorical=True
    )

    model = xgb.Booster()
    model.load_model(model_path)

    scores = model.predict(dtest)
    df_test["scores"] = scores
    df_test.to_csv(PREDICTION_PATH)

    print("Done.")
