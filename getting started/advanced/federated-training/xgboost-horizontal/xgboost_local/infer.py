import pandas as pd
import xgboost as xgb

from config import (
    TEST_DATA_PATH,
    MODEL_PATH,
    PREDICTION_PATH,
    NUMERIC_COLS,
    CATEGORICAL_COLS,
    LABEL_COL,
)

if __name__ == "__main__":
    df_test = pd.read_csv(TEST_DATA_PATH)
    numeric = df_test[NUMERIC_COLS].astype("float")
    categorical = df_test[CATEGORICAL_COLS].astype("category")
    labels = df_test[LABEL_COL].astype("int")
    dtest = xgb.DMatrix(
        pd.concat([numeric, categorical], axis=1), enable_categorical=True
    )

    model = xgb.Booster()
    model.load_model(MODEL_PATH)

    scores = model.predict(dtest)
    df_test["scores"] = scores
    df_test.to_csv(PREDICTION_PATH)

    print("Done.")
