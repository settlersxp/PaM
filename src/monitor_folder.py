import os
import time
import subprocess
import logging
import sys
from deployment_utils import register_logger, get_folder_hash, CLONED_PROJECT_PATH

# Setup logging
logger = register_logger('monitor_folder')

CHECK_INTERVAL = 10  # seconds
LAST_HASH_FILE = "last_folder_hash.txt"


def save_hash(folder_hash):
    """Save the current folder hash"""
    with open(LAST_HASH_FILE, 'w') as f:
        f.write(folder_hash)


def get_saved_hash():
    """Get the last saved folder hash"""
    try:
        with open(LAST_HASH_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def run_setup_scripts(scripts):
    """Run setup_env.py, setup_db.py and run_server.py"""
    
    for script in scripts:
        if not os.path.exists(script):
            logging.error(f"Script {script} not found!")
            continue
            
        logging.info(f"Running {script}...")
        try:
            # Use python executable from system path
            python_exe = sys.executable
            result = subprocess.run(
                [python_exe, script],
                check=True,
                capture_output=True,
                text=True
            )
            logging.info(f"{script} output:\n{result.stdout}")
            if result.stderr:
                logging.warning(f"{script} errors:\n{result.stderr}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error running {script}: {e}")
            logging.error(f"Script output:\n{e.output}")
            continue
        except Exception as e:
            logging.error(f"Unexpected error running {script}: {e}")
            continue

        logging.info(f"Successfully completed {script}")


def main():
    logging.info("Starting folder monitor")

    while True:
        try:
            # Get current folder hash
            current_hash = get_folder_hash(logger, CLONED_PROJECT_PATH)
            saved_hash = get_saved_hash()

            # Check if folder exists
            if current_hash is None:
                logging.info(f"Folder {CLONED_PROJECT_PATH} does not exist")
                time.sleep(CHECK_INTERVAL)
                continue

            # If this is the first time we're seeing the folder
            if saved_hash is None:
                logging.info("Folder created for the first time")
                run_setup_scripts(scripts=[
                    'setup_env.py',
                    f'{CLONED_PROJECT_PATH}/setup_env.py',
                    f'{CLONED_PROJECT_PATH}/setup_db.py'
                ])
                save_hash(current_hash)

            # If the folder has been modified
            elif current_hash != saved_hash:
                logging.info("Folder contents have changed")
                run_setup_scripts(scripts=[
                    f'{CLONED_PROJECT_PATH}/setup_env.py',
                    f'{CLONED_PROJECT_PATH}/setup_db.py'
                ])
                save_hash(current_hash)

            # Wait for next check
            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            logging.info("Monitor stopped by user")
            break
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
