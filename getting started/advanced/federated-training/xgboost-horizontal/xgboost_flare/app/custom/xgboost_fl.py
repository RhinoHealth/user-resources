import json
from pathlib import Path

import pandas as pd
import xgboost as xgb

# (1) import nvflare client API
from nvflare import client as flare
from nvflare.app_opt.xgboost.tree_based.shareable_generator import update_model

from fl_config import (
    NUMERIC_COLS,
    CATEGORICAL_COLS,
    LABEL_COL,
    NUM_ROUNDS,
)

data_dirs = [x for x in Path("/input/datasets/").iterdir() if x.resolve().is_dir()]
TRAIN_DATA_PATH = Path(data_dirs[0] / "dataset.csv")

if __name__ == "__main__":
    # (2) initializes NVFlare client API
    flare.init()

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

    global_model_as_dict = None
    acc = 0
    while flare.is_running():
        # (3) receives FLModel from NVFlare
        input_model = flare.receive()
        global_params = input_model.params
        curr_round = input_model.current_round

        print(f"current_round={curr_round}")
        if curr_round == 0:
            # (4) first round, no global model
            model = xgb.train(xgb_params, dtrain, NUM_ROUNDS, evals=[(dtrain, "train")])
            config = model.save_config()
        else:
            # (5) update model based on global updates
            model_updates = global_params["model_data"]
            for update in model_updates:
                global_model_as_dict = update_model(
                    global_model_as_dict, json.loads(update)
                )
            loadable_model = bytearray(json.dumps(global_model_as_dict), "utf-8")
            # load model
            model.load_model(loadable_model)
            model.load_config(config)

            # get model accuracy for metrics
            acc = sum(model.predict(dtrain).round() == df_train[LABEL_COL]) / len(
                df_train[LABEL_COL]
            )

            # (6) train model in two steps
            # first, eval on train and test
            eval_results = model.eval_set(
                evals=[(dtrain, "train")], iteration=model.num_boosted_rounds() - 1
            )
            print(eval_results)
            # second, train for one round
            model.update(dtrain, model.num_boosted_rounds())

        # (7) construct trained FL model
        # Extract newly added tree using xgboost_bagging slicing api
        bst_new = model[model.num_boosted_rounds() - 1 : model.num_boosted_rounds()]
        local_model_update = bst_new.save_raw("json")
        params = {"model_data": local_model_update}
        metrics = {"accuracy": acc}

        output_model = flare.FLModel(params=params, metrics=metrics)

        # (8) send model back to NVFlare
        flare.send(output_model)

    print("Done.")
