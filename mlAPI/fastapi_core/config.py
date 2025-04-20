from pathlib import Path
from starlette.config import Config
from starlette.datastructures import Secret
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

APP_VERSION = "1.0"
APP_NAME = "Findex Visualizer"
API_PREFIX = "/api"
BASE_DIR = Path(__file__).resolve().parent

env_path = BASE_DIR / '.env'
config = Config(env_path)
# API_KEY: Secret = config("API_KEY", cast=Secret)
API_KEY: Secret = config("API_KEY", cast=Secret, default="dev-secret")
IS_DEBUG: bool = config("IS_DEBUG", cast=bool, default=False)


STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
def configure_static(app):
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    
MODEL_DIR = BASE_DIR / "models"
LOG_DIR = BASE_DIR / "logs"

PARENT_DIR = Path(__file__).parent.parent
DATA_DIR = PARENT_DIR / "data"
OUTPUT_DIR = PARENT_DIR / "outputs"

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

ETL_SESSIONS = {}  
TRAIN_SESSIONS = {}  
SESSION_COUNTER = {} 