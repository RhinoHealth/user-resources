import sys
import pandas as pd
import xgboost as xgb


def infer(model_weights_file_path):
    df = pd.read_csv("/input/cohort_data.csv")
    X_test = df.drop('outcome', axis=1).values
    dtest = xgb.DMatrix(X_test)
    # Inference: Apply model and add predictions column.
    bst = xgb.Booster()  # init model
    bst.load_model(model_weights_file_path)  # load model
    y_pred = bst.predict(dtest)
    df['model_score'] = y_pred
    df.to_csv("/output/cohort_data.csv", index=False)


if __name__ == "__main__":

    args = sys.argv[1:]
    (model_weights_file_path,) = args
    infer(model_weights_file_path)
    sys.exit(0)
