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

import re
import threading
from typing import Optional


class WeightedAggregationHelper(object):
    def __init__(self, exclude_vars: Optional[str] = None, weigh_by_local_iter: bool = True):
        """Perform weighted aggregation.

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
        self.samples = []
        self.data = []

    def reset_stats(self):
        self.total = dict()
        self.counts = dict()
        self.history = list()
        self.samples = []
        self.data = []

    def add(self, data, contributor_name, contribution_round, n_samples):
        """Compute weighted sum and sum of weights."""
        with self.lock:
            self.samples.append(n_samples)
            self.data.append(data)

            self.history.append(
                {
                    "contributor_name": contributor_name,
                    "round": contribution_round,
                    "n_samples": n_samples,
                }
            )

    def get_result(self):
        """Compute aggregated weights based on amount of samples per client."""
        with self.lock:
            total = sum(self.samples)
            self.weights = [value / total for value in self.samples]
            for i in range(len(self.data)):
                for k, v in self.data[i].items():
                    if self.exclude_vars is not None and self.exclude_vars.search(k):
                        continue
                    weighted_value = v * self.weights[i]
                    current_total = self.total.get(k, None)
                    if current_total is None:
                        self.total[k] = weighted_value
                        self.counts[k] = self.weights[i]
                    else:
                        self.total[k] = current_total + weighted_value
                        self.counts[k] = self.counts[k] + self.weights[i]

            aggregated_dict = {k: v * (1.0 / self.counts[k]) for k, v in self.total.items()}
            self.reset_stats()
            return aggregated_dict

    def get_history(self):
        return self.history

    def get_len(self):
        return len(self.get_history())