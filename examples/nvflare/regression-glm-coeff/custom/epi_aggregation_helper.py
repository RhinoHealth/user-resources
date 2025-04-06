# Copyright (c) 2023, Rhino HealthTech, Inc.
# Original file modified by Rhino Health to adapt it to the Rhino Health Federated Computing Platform.

# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
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

import numpy as np
import re
import threading
from typing import Optional

from coeff_optimizer import OPTIMIZERS


class EPIAggregationHelper(object):
    def __init__(self, exclude_vars: Optional[str] = None, weigh_by_local_iter: bool = True,
                 target_accuracy: float = None):
        """Perform aggregation by the chosen optimization method.

        Args:
            exclude_vars (str, optional): regex string to match excluded vars during aggregation. Defaults to None.
            weigh_by_local_iter (bool, optional): Whether to weight the contributions by the number of iterations
                performed in local training in the current round. Defaults to `True`.
                Setting it to `False` can be useful in applications such as homomorphic encryption to reduce
                the number of computations on encrypted ciphertext.
                The aggregated sum will still be divided by the provided weights and `aggregation_weights` for the
                resulting weighted sum to be valid.
        """
        super().__init__()
        self.lock = threading.Lock()
        self.exclude_vars = re.compile(exclude_vars) if exclude_vars else None
        self.weigh_by_local_iter = weigh_by_local_iter
        self.reset_stats()
        self.total = dict()
        self.counts = dict()
        self.history = list()
        self.accuracy_threshold = None
        self.target_accuracy = target_accuracy
        self.add_results = dict()
        self.contribution_round = None
        self.betas_list = list()
        self.method = None
        self.optimizer = None
        self.exog_names = None
        self.abort_signal = False
        self.last_result = None

    def reset_stats(self):
        self.total = dict()
        self.counts = dict()
        self.history = list()

    def verify_exog_names(self, data):
        current_exog_names = data.get("exog_names")
        if current_exog_names is None:
            return True
        if self.exog_names is None:
            self.exog_names = current_exog_names
            return True
        elif self.exog_names != current_exog_names:
            print(f"exog_names mismatch: {self.exog_names} != {current_exog_names}")
            return False
        else:
            self.exog_names = current_exog_names
            return True

    def set_optimization_method(self, data):
        if not self.method:
            try:
                # The method is initialized by the client - set server config accordingly
                self.method = data.get("method")
                self.optimizer = OPTIMIZERS[self.method]()
                self.add_results = self.optimizer.get_add_results_base_dict()
            except KeyError:
                raise ValueError(f"No optimizer found for method: {self.method}.")

    def add(self, data, weight, contributor_name, contribution_round):
        # TODO - Contribution round minus 1??
        """Compute sum of weights."""
        self.contribution_round = contribution_round
        with self.lock:
            self.optimizer.add(data, self.add_results, contribution_round)
        # TODO change this to condition not if abort signal
        self.history.append(
            {
                "contributor_name": contributor_name,
                "round": contribution_round,
                "weight": weight,
            }
        )

    def get_result(self):
        # Ori here is the aggregation from all sites
        # Ori - Check if already optimized - calculate AIC for the model the get_results shouldn't triggered but the aic
        """If already aborted"""
        if self.abort_signal:
            result = self.last_result
            k = len(self.last_result["beta"])  # number of parameters
            aic = 2 * k - 2 * self.add_results["log_likelihood_sum"]
            result["aic"] = aic
            print('CHECK AIC : ', result)
            return result

        """Aggregate from all sites"""
        with self.lock:
            accuracy_threshold, result = self.optimizer.get_result(self.add_results, self.contribution_round,
                                                                   self.target_accuracy, betas_list=self.betas_list,
                                                                   accuracy_threshold=self.accuracy_threshold)
            if result.get("signal") == "ABORT":
                self.abort_signal = True
                self.last_result = result
            self.accuracy_threshold = accuracy_threshold  # This is only relevant for NR optimizer
            self.reset_stats()
            return result

    def get_history(self):
        return self.history

    def get_len(self):
        return len(self.get_history())