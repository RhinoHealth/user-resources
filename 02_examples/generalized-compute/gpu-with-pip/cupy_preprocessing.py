import cupy as cp
import pandas as pd
import os
import cv2
from sklearn.model_selection import train_test_split

path = '/input/file_data/'

idx_elements = {k: v for (k, v) in enumerate(list(os.walk(path))[0][1])}
elements_idx = {v: k for (k, v) in enumerate(list(os.walk(path))[0][1])}

# one hot using cupy
features = []
labels = []
for folder in list(os.walk(path))[1:]:
    feature = folder[0].split('/')[-1]
    for img_path in folder[2]:
        features.append(cv2.resize(cv2.imread(path + feature + "/" + img_path), (28, 28)))
        one_hot = cp.zeros(len(idx_elements))
        one_hot[elements_idx[feature]] = 1
        labels.append(one_hot)
features = cp.array(features)
labels = cp.array(labels)

# normalize
features = features / 255.0
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.33, random_state=42)

# Write data to /output
cp.save('/output/file_data/X_train', X_train)
cp.save('/output/file_data/y_train', y_train)
cp.save('/output/file_data/X_test', X_test)
cp.save('/output/file_data/y_test', y_test)

df = pd.DataFrame()
df = df.append({'X_train': 'X_train.npy', 'X_test': 'X_test.npy',
                'y_train': 'y_train.npy', 'y_test': 'y_test.npy'}, ignore_index=True)

df.to_csv('/output/dataset.csv')
