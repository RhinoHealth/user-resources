# Copyright (c) 2023, Rhino HealthTech, Inc.
# Original file modified by Rhino Health to adapt it to the Rhino Health Federated Computing Platform.

# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
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


import copy
from typing import Optional, Tuple
import pandas as pd
import numpy as np
import os
from sklearn.linear_model import QuantileRegressor
from sklearn.model_selection import train_test_split

from nvflare.apis.fl_context import FLContext
from nvflare.app_common.abstract.learner_spec import Learner


class QuantileLearner(Learner):
    def __init__(
        self,
        data_path: str,
        test_size: float = None,
        random_state: int = None,
        feature_columns: list = None,
        label_column: str = None,
        max_iter: int = 1,
    ):
        super().__init__()
        self.data_path = data_path
        self.random_state = random_state
        self.test_size = test_size
        self.feature_columns = feature_columns
        self.label_column = label_column
        self.max_iter = max_iter
        self.n_samples = None
        self.local_model = None
        self.n_features = None
        self.X_train = None
        self.y_train = None
        self.X_valid = None
        self.y_valid = None

    def load_data(self):
        # Get data
        dataset_uid = next(os.walk(self.data_path))[1][0]
        if self.feature_columns:
            self.feature_columns.append(self.label_column)
            df_train = pd.read_csv(f'{self.data_path}/{dataset_uid}/dataset.csv', usecols=self.feature_columns)
        else:
            df_train = pd.read_csv(f'{self.data_path}/{dataset_uid}/dataset.csv')
        x_valid, y_valid = None, None
        if self.test_size > 0:
            df_train, df_valid = train_test_split(df_train, test_size=self.test_size, random_state=self.random_state)
            x_valid = df_valid.drop(self.label_column, axis=1).values
            y_valid = df_valid[self.label_column].values

        x_train = df_train.drop(self.label_column, axis=1).values
        y_train = df_train[self.label_column].values
        return x_train, y_train, x_valid, y_valid

    def initialize(self, fl_ctx: FLContext):
        self.log_info(fl_ctx, f"Loading data from {self.data_path}")
        self.X_train, self.y_train, self.X_valid, self.y_valid = self.load_data()
        # train data size, to be used for setting
        self.n_samples = self.X_train.shape[0]
        self.n_features = self.X_train.shape[1]
        # model will be created after receiving global parameters

    def set_parameters(self, params):
        self.local_model.coef_ = params["coef"]
        if self.local_model.fit_intercept:
            self.local_model.intercept_ = params["intercept"]

    def train(self, curr_round: int, global_param: Optional[dict], fl_ctx: FLContext) -> Tuple[dict, dict]:
        if curr_round == 0:
            # initialize model with global_param
            # and set to all zero
            self.local_model = QuantileRegressor(
                quantile=global_param["quantile"],
                alpha=global_param["alpha"],
                fit_intercept=bool(global_param["fit_intercept"]),
                solver=global_param["solver"],
                solver_options=global_param.get("solver_options"),
            )
            n_classes = global_param["n_classes"]
            self.local_model.classes_ = np.array(list(range(n_classes)))
            self.local_model.coef_ = np.zeros((1, self.n_features))
            if global_param["fit_intercept"]:
                self.local_model.intercept_ = np.zeros((1,))

        # Training starting from global model
        # Note that the parameter update using global model has been performed
        # during global model evaluation
        self.local_model.fit(self.X_train, self.y_train)
        if self.local_model.fit_intercept:
            params = {
                "coef": self.local_model.coef_,
                "intercept": self.local_model.intercept_,
            }
        else:
            params = {"coef": self.local_model.coef_}

        return copy.deepcopy(params), self.local_model

    def finalize(self, fl_ctx: FLContext):
        # freeing resources in finalize
        self.log_info(fl_ctx, "Freed training resources")
