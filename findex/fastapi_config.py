from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Directory paths
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
OUTPUT_DIR = BASE_DIR / "outputs"
LOG_DIR = BASE_DIR / "logs"

# File paths
TRAIN_PATH_2017 = DATA_DIR / "findex2017_micro_world.csv"
TRAIN_PATH_2021 = DATA_DIR / "findex2021_micro_world_139countries.csv"
TEST_PATH = DATA_DIR / "test.csv"
PROCESSED_TEST_PATH = DATA_DIR / "test_processed.csv"

# Ensure directories exist on import
DATA_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)