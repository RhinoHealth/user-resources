# Copyright (c) 2023, Rhino HealthTech, Inc.
# Original file modified by Rhino Health to adapt it to the Rhino Health Federated Computing Platform.

# Copyright (c) 2021, NVIDIA CORPORATION.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pandas as pd
import xgboost as xgb

from nvflare.app_common.app_constant import AppConstants
from nvflare.app_opt.xgboost.tree_based.executor import FedXGBTreeExecutor

import os
from sklearn.model_selection import train_test_split

def load_client_data():
    # Get cohort data
    cohorts_path = '/input/cohorts'
    cohort_uid = next(os.walk(cohorts_path))[1][0]
    df = pd.read_csv(f'{cohorts_path}/{cohort_uid}/cohort_data.csv')
    df_train, df_valid = train_test_split(df, test_size=0.25, random_state=42)
    X_train = df_train.drop('outcome', axis=1).values
    X_valid = df_valid.drop('outcome', axis=1).values
    y_train = df_train['outcome'].values
    y_valid = df_valid['outcome'].values
    return X_train, y_train, X_valid, y_valid, len(y_train)

class FedXGBTreeBCWExecutor(FedXGBTreeExecutor):
    def __init__(
        self,
        training_mode,
        lr_scale = 0.5,
        num_tree_bagging: int = 1,
        lr_mode: str = "uniform",
        local_model_path: str = "model.json",
        global_model_path: str = "model_global.json",
        learning_rate: float = 0.1,
        objective: str = "binary:logistic",
        max_depth: int = 8,
        eval_metric: str = "auc",
        nthread: int = 16,
        tree_method: str = "hist",
        train_task_name: str = AppConstants.TASK_TRAIN,
    ):
        super().__init__(
            training_mode=training_mode,
            num_tree_bagging=num_tree_bagging,
            lr_scale=lr_scale,
            lr_mode=lr_mode,
            local_model_path=local_model_path,
            global_model_path=global_model_path,
            learning_rate=learning_rate,
            objective=objective,
            max_depth=max_depth,
            eval_metric=eval_metric,
            nthread=nthread,
            tree_method=tree_method,
            train_task_name=train_task_name,
        )

    def load_data(self):

        # load cohorts
        X_train, y_train, X_valid, y_valid, sample_size = load_client_data()

        # training
        dmat_train = xgb.DMatrix(X_train, label=y_train)

        # validation
        dmat_valid = xgb.DMatrix(X_valid, label=y_valid)

        return dmat_train, dmat_valid
