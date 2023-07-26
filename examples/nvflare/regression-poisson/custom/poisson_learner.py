import copy
from typing import Optional, Tuple
import pandas as pd
import numpy as np
import os
# from sklearn.linear_model import SGDClassifier
from sklearn.linear_model import PoissonRegressor
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

from nvflare.apis.fl_context import FLContext
from nvflare.app_common.abstract.learner_spec import Learner


class PoissonLearner(Learner):
    def __init__(
        self,
        data_path: str,
        test_size: float = None,
        random_state: int = None,
        features_columns: list = [],
        label_column: str = None,
        max_iter: int = 1,
    ):
        super().__init__()
        self.data_path = data_path
        self.random_state = random_state
        self.test_size = test_size
        self.features_columns = features_columns
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
        # Get cohort data
        cohort_uid = next(os.walk(self.data_path))[1][0]
        if self.features_columns:
            self.features_columns.append(self.label_column)
            df_train = pd.read_csv(f'{self.data_path}/{cohort_uid}/cohort_data.csv', usecols=self.features_columns)
        else:
            df_train = pd.read_csv(f'{self.data_path}/{cohort_uid}/cohort_data.csv')
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
            # fit_intercept = bool(global_param["fit_intercept"])
            self.local_model = PoissonRegressor(
                alpha=global_param["alpha"],
                fit_intercept=global_param["fit_intercept"],
                solver=global_param["solver"],
                tol=global_param["tol"],
                max_iter=self.max_iter,
                warm_start=False,
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

        # if self.X_valid is not None:
        #     y_pred = self.local_model.predict(self.X_valid)
        #     auc = roc_auc_score(self.y_valid, y_pred)
        #     self.log_info(fl_ctx, f"AUC {auc:.4f}")
        #     metrics = {"AUC": auc}

        return copy.deepcopy(params), self.local_model

    def finalize(self, fl_ctx: FLContext):
        # freeing resources in finalize
        self.log_info(fl_ctx, "Freed training resources")
