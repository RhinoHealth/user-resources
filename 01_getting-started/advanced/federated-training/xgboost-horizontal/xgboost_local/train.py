import pandas as pd
import xgboost as xgb

from config import (
    TRAIN_DATA_PATH,
    MODEL_PATH,
    NUMERIC_COLS,
    CATEGORICAL_COLS,
    LABEL_COL,
    NUM_ROUNDS,
)

if __name__ == "__main__":
    df_train = pd.read_csv(TRAIN_DATA_PATH)
    numeric = df_train[NUMERIC_COLS].astype("float")
    categorical = df_train[CATEGORICAL_COLS].astype("category")
    labels = df_train[LABEL_COL].astype("int")
    dtrain = xgb.DMatrix(
        pd.concat([numeric, categorical], axis=1),
        label=labels,
        enable_categorical=True,
    )

    xgb_params = {"objective": "binary:logistic"}

    model = xgb.train(xgb_params, dtrain, NUM_ROUNDS, evals=[(dtrain, "train")])

    model.save_model(MODEL_PATH)

    print("Done.")
