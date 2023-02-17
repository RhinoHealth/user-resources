from pathlib import Path

import pandas as pd
import pydicom
import numpy as np
from PIL import Image


def extract_dcm_pixel_array_as_image(dicom):
    im = dicom.pixel_array.astype(float)
    rescaled_image = (np.maximum(im, 0)/im.max())*255  # float pixels
    final_image = np.uint8(rescaled_image)  # integers pixels
    final_image = Image.fromarray(final_image)
    return final_image


if __name__ == '__main__':
    df_cohort = pd.read_csv('/input/cohort_data.csv', dtype={'SOPInstanceUID': str})
    inputdir = Path('/input/dicom_data/')
    outdir = Path('/output/file_data/')

    dcm_file_paths = list(inputdir.glob('*.[dD][cC][mM]'))
    for dcm_file_path in dcm_file_paths:
        dicom = pydicom.dcmread(dcm_file_path)
        image = extract_dcm_pixel_array_as_image(dicom)
        png_file_name = dcm_file_path.with_suffix('.png')
        # insert the png file name based on the SOPInstanceUID in df_cohort
        idx = df_cohort['Pneumonia'][df_cohort.SOPInstanceUID == dicom.SOPInstanceUID].index[0]
        ground_truth = str(df_cohort.loc[idx, 'Pneumonia'])
        outfile = outdir / ground_truth / png_file_name
        outfile.parent.mkdir(parents=True, exist_ok=True)
        image.save(str(outfile))
        df_cohort.loc[idx, 'PNG_file'] = str(outfile.relative_to(outdir)).replace('\\', '/')

    df_cohort.drop('SOPInstanceUID', axis=1, inplace=True)
    df_cohort.to_csv('/output/cohort_data.csv', index=False)
