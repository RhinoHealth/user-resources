from pathlib import Path
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
import tensorflow as tf
tf.get_logger().setLevel('ERROR')

# Defining Train Data Path
TRAIN_DATA_DIR = Path("/input/datasets/")

# Dataset Config
FEATURE_COLUMNS = [f'X{i}' for i in range(1, 1025)]
INPUT_FEATURE_SIZE = len(FEATURE_COLUMNS)
TARGET_COLUMN = 'y'
SMILES_ID_COLUMN = 'ids'
