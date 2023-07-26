
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
