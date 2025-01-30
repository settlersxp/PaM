import logging
import platform
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deployment_utils.log'),
        logging.StreamHandler()
    ]
)

is_windows = platform.system().lower() == "windows"
venv_folder_name = "venv"
base_path = os.path.dirname(os.path.abspath(__file__))
folders = base_path.split(os.sep)
CLONED_PROJECT_PATH = os.path.join(str.join(os.sep, folders[:-2]), "SimpleTradingFramework")
ENV_PATH_OF_CLONED_PROJECT = os.path.join(CLONED_PROJECT_PATH, venv_folder_name)


def register_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.FileHandler(f'{logger_name}.log'))
    logger.addHandler(logging.StreamHandler())
    return logger