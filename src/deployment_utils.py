import logging
import subprocess
import platform
import sys
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


def run_command_as_subprocess_with_stream(command, local_logging):
    try:
        # Use subprocess.Popen to keep the server running
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )

        # Stream the output in real-time
        while True:
            output = process.stdout.readline()
            if output:
                local_logging.info(output.strip())
            error = process.stderr.readline()
            if error:
                local_logging.error(error.strip())

            # Check if process has ended
            if output == '' and error == '' and process.poll() is not None:
                break

        return process.poll() == 0
    except Exception as e:
        local_logging.error(f"Command failed: {e}")
        return False


def is_command_found(command):
    try:
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def has_venv(project_path=None):
    if project_path is None:
        project_path = base_path

    venv_path = os.path.join(project_path, venv_folder_name)
    return os.path.exists(venv_path)


def get_venv_path(local_logging, project_path=None):
    if project_path is None:
        project_path = base_path

    venv_path = os.path.join(project_path, venv_folder_name)
    
    # Check if virtual environment exists
    if not os.path.exists(venv_path):
        local_logging.error(f"Virtual environment not found at {venv_path}")
        sys.exit(1)

    # Construct the activation command based on OS
    if is_windows:
        activate_cmd = f"{venv_path}\\Scripts\\activate"
        python_cmd = f"{venv_path}\\Scripts\\python"
    else:
        activate_cmd = f"source {venv_path}/bin/activate"
        python_cmd = f"{venv_path}/bin/python"
    
    return activate_cmd, python_cmd


def check_pip(local_logging):
    """Check if pip or pip3 exists and return the working command"""
    if is_command_found("pip --version"):
        return "pip"
    elif is_command_found("pip3 --version"):
        return "pip3"
    else:
        local_logging.error("Error: Neither pip nor pip3 is installed.")
        sys.exit(1)


def check_python(local_logging):
    if is_command_found("python --version"):
        return "python"
    elif is_command_found("python3 --version"):
        return "python3"
    else:
        local_logging.error("Error: Neither python nor python3 is installed.")
        sys.exit(1)


def create_and_install_venv(local_logging, project_path=None):
    if project_path is None:
        project_path = base_path

    pip_cmd = check_pip(local_logging)
    python_cmd = check_python(local_logging)
    if not is_command_found(f"{pip_cmd} install virtualenv"):
        local_logging.error("Error: Failed to install virtualenv")
        sys.exit(1)
    
    if not is_command_found(f"{python_cmd} -m venv {os.path.join(project_path, venv_folder_name)}"):
        local_logging.error("Error: Failed to create virtual environment")
        sys.exit(1)


def install_requirements(local_logging, activate_cmd, python_cmd):
    # Activate virtual environment and install requirements
    pip_install_cmd = f"{python_cmd} -m pip install -r requirements.txt"

    # Combine commands
    if is_windows:
        full_command = f"{activate_cmd} && {pip_install_cmd}"
    else:
        full_command = f"{activate_cmd} && {pip_install_cmd}"

    local_logging.info(f"Activating virtual environment and "
                       f"installing requirements... {full_command}")
    if not is_command_found(full_command):
        local_logging.error("Error: Failed to install requirements")
        sys.exit(1)