from pathlib import Path
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
import tensorflow as tf
tf.get_logger().setLevel('ERROR')

# Defining Test Data Path
TEST_DATA_PATH = "../../data/BACE/test_df.csv"

# Defining Output Paths
MODEL_PARAMS_PATH = Path("../saved_models/local_simulation.pt")
PREDS_PATH = Path("../../results/local_simulation_preds.csv")

# Dataset Config
FEATURE_COLUMNS = [f'X{i}' for i in range(1, 1025)]
INPUT_FEATURE_SIZE = len(FEATURE_COLUMNS)
TARGET_COLUMN = 'y'
SMILES_ID_COLUMN = 'ids'

# Function to get the site dataset for simulated NVFlare training
def get_site_dataset(site):
    TRAIN_DATA_DIR = Path(f"../../../../data/BACE/{site}")
    return TRAIN_DATA_DIR