import sys
import pandas as pd
import os
import glob


def infer():

    run_inference = 'python -m monai.bundle run evaluating ' \
                    '--meta_file /home/localuser/config/spleen_ct_segmentation/configs/metadata.json ' \
                    '--config_file /home/localuser/config/spleen_ct_segmentation/configs/inference.json ' \
                    '--logging_file /home/localuser/config/spleen_ct_segmentation/configs/logging.conf'
    os.system(run_inference)
    df = pd.read_csv("/input/dataset.csv")
    images = list(df.image.values)
    images.sort()
    segmentations = [i.replace('/output/file_data/', '') for i in list(glob.glob('/output/file_data/seg_out/*/*'))]
    segmentations.sort()
    df = pd.DataFrame({'image': images, 'segmentation': segmentations})
    df.to_csv("/output/dataset.csv", index=False)


if __name__ == "__main__":

    infer()
    sys.exit(0)

