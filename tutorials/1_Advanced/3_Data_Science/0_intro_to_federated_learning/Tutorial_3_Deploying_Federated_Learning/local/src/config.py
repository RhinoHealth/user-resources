from pathlib import Path
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
import tensorflow as tf
tf.get_logger().setLevel('ERROR')

# Define Training Site
SITE = "site-3" # MUST DEFINE SITE ∈ {"site-1", "site-2", "site-3", "centralized"}
assert SITE in {"site-1", "site-2", "site-3", "centralized"}, f"Invalid SITE: {SITE}"

# Defining Train Data Path
TRAIN_DATA_DIR = Path(f"../../data/BACE/{SITE}")

# Defining Test Data Path
TEST_DATA_PATH = "../../data/BACE/test_df.csv"

# Defining Output Paths
MODEL_PARAMS_PATH = Path(f"../saved_models/local_{SITE}.pt")
PREDS_PATH = Path(f"../../results/local_{SITE}_preds.csv")

# Dataset Config
FEATURE_COLUMNS = [f'X{i}' for i in range(1, 1025)]
INPUT_FEATURE_SIZE = len(FEATURE_COLUMNS)
TARGET_COLUMN = 'y'
SMILES_ID_COLUMN = 'ids'