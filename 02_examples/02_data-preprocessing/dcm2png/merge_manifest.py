#!/usr/bin/env python
# coding: utf-8
import pandas as pd
import os
import numpy as np
import copy
import argparse
import sys

parser = argparse.ArgumentParser(description = 'merge manifest')

parser.add_argument('--ehr_csv', type=str, required=True, help="raw EHR data csv")
parser.add_argument('--manifest_csv', type=str, required=True, help="CXR manifest csv")
parser.add_argument('--merged_csv', type=str, required=True, help="merged manifest csv")

args = parser.parse_args()

for k in vars(args):
    print (k, '=', vars(args)[k])

manifest_paths = [args.manifest_csv]
manifests = []
for path in manifest_paths:
    df = pd.read_csv(path, dtype={'SeriesInstanceUID': str, 'StudyInstanceUID': str, 'filename': str})
    df['folder'] = [os.path.dirname(path)] * len(df)
    manifests.append(df)
df_imgs = pd.concat(manifests, ignore_index=True)

df_annotations = pd.read_csv(args.ehr_csv, dtype={'ID_XR_SUID': str})

records = []
for i, row in df_annotations.iterrows():
    suid = row['ID_XR_SUID']
    sub_df_img = df_imgs[(df_imgs.SeriesInstanceUID == suid)]
    if len(sub_df_img) == 0:
        #records.append(row)
        pass
    else:
        for k, rrow in sub_df_img.iterrows():
            row['filename'] = rrow['filename']
            #row['folder'] = rrow['folder']
            for field in [
                'ImageType',
                'BodyPartExamined',
                'Manufacturer',
                'ExposureIndex',
                'PixelSpacing',
                'ProtocolName',
                'SeriesDescription',
                'AcquisitionDeviceProcessingDescription',
            ]:
                row[field] = rrow[field]
            records.append(row)

df = pd.DataFrame(records)

df.to_csv(args.merged_csv, index=False)

