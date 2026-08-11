import pandas as pd
import numpy as np
from PIL import Image
import os
import shutil


def extract_label(filename):
    basename = os.path.basename(filename)
    return basename.split('_label_')[-1].replace('.png', '')


def extract_pooled_features(image_path, pool_size=8):
    img = np.array(Image.open(image_path).convert('L'))
    h, w = img.shape
    pooled = img.reshape(h // pool_size, pool_size, w // pool_size, pool_size).mean(axis=(1, 3))
    return pooled.flatten()


if __name__ == '__main__':
    dataset = pd.read_csv('/input/0/dataset.csv')

    input_base = '/input/0/file_data/'
    pool_size = 8
    records = []

    for _, row in dataset.iterrows():
        filename = row['Filename']
        input_path = os.path.join(input_base, filename)

        label = extract_label(filename)
        pixels = extract_pooled_features(input_path, pool_size)

        record = {'Filename': filename, 'label': label}
        record.update({f'pixel_{i}': val for i, val in enumerate(pixels)})
        records.append(record)

    output_df = pd.DataFrame(records)

    pixel_cols = [col for col in output_df.columns if col.startswith('pixel_')]
    output_df['mean_intensity'] = output_df[pixel_cols].mean(axis=1)
    output_df['std_intensity'] = output_df[pixel_cols].std(axis=1)
    output_df['min_intensity'] = output_df[pixel_cols].min(axis=1)
    output_df['max_intensity'] = output_df[pixel_cols].max(axis=1)
    output_df['median_intensity'] = output_df[pixel_cols].median(axis=1)

    # Subsample into two datasets per split
    split_col = output_df['Filename'].apply(lambda f: os.path.basename(f).split('_')[0])
    
    df0_parts, df1_parts = [], []
    for split, group in output_df.groupby(split_col):
        half = len(group) // 2
        df0_parts.append(group.iloc[:half])
        df1_parts.append(group.iloc[half:])

    df0 = pd.concat(df0_parts).reset_index(drop=True)
    df1 = pd.concat(df1_parts).reset_index(drop=True)

    # Copy images to both outputs
    for output_idx in ['0', '1']:
        output_img_base = f'/output/{output_idx}/file_data/'
        for filename in output_df['Filename']:
            src = os.path.join(input_base, filename)
            dst = os.path.join(output_img_base, filename)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)

    # Save CSVs
    os.makedirs('/output/0/', exist_ok=True)
    os.makedirs('/output/1/', exist_ok=True)
    df0.to_csv('/output/0/dataset.csv', index=False)
    df1.to_csv('/output/1/dataset.csv', index=False)