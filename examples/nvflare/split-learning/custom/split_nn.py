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

from moderate_cnn import ModerateCNN
import glob
import os


class SplitNN(ModerateCNN):
    def __init__(self):
        super().__init__()
        cohort_uid = next(os.walk('/input/cohorts'))[1][0]
        cohort_files = glob.glob('/input/cohorts/' + cohort_uid + '/file_data/*')
        for file in cohort_files:
            if 'data_site1' in file:
                split_id = 0
            elif 'data_site2' in file:
                split_id = 1

        if split_id not in [0, 1]:
            raise ValueError(f"Only supports split_id '0' or '1' but was {self.split_id}")
        self.split_id = split_id

        if self.split_id == 0:
            self.split_forward = self.conv_layer
        elif self.split_id == 1:
            self.split_forward = self.fc_layer
        else:
            raise ValueError(f"Expected split_id to be '0' or '1' but was {self.split_id}")

    def forward(self, x):
        x = self.split_forward(x)
        return x

    def get_split_id(self):
        return self.split_id
