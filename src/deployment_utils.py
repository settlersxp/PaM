import logging
import subprocess
import platform
import sys
import os
import signal
import hashlib

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


def get_venv_path(local_logging):
    base_path = os.path.dirname(os.path.abspath(__file__))
    venv_path = os.path.join(base_path, venv_folder_name)
    
    env_found = False
    # Check if virtual environment exists
    if os.path.exists(venv_path):
        local_logging.error(f"Virtual environment not found at {venv_path}")
        env_found = True
    
    # Split the path into folders and check if the env file is not 1 folder outside of the current location
    folders = base_path.split(os.sep)[:-1]
    if os.path.exists(os.path.join(os.sep, *folders, "venv")):
        venv_path = os.path.join(os.sep, *folders, venv_folder_name)
        local_logging.error("Error: env file not found in the parent folder")
        env_found = True

    if not env_found:
        local_logging.error("Error: env file not found.")
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


def create_and_install_venv(local_logging):
    pip_cmd = check_pip(local_logging)
    python_cmd = check_python(local_logging)
    if not is_command_found(f"{pip_cmd} install virtualenv"):
        local_logging.error("Error: Failed to install virtualenv")
        sys.exit(1)
    
    if not is_command_found(f"{python_cmd} -m venv {venv_folder_name}"):
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


def kill_python_process(local_logging, process_name):
    import psutil

    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Check if this is our Flask app
            if proc.info['cmdline'] and 'python' in proc.info['cmdline'][0] and process_name in proc.info['cmdline'][-1]:
                local_logging.info(f"Killing {process_name} process (PID: {proc.info['pid']})")
                if is_windows:
                    subprocess.run(['taskkill', '/F', '/PID', str(proc.info['pid'])])
                else:
                    os.kill(proc.info['pid'], signal.SIGTERM)
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def get_folder_hash(local_logging, folder_path):
    """Calculate hash of the entire folder contents, excluding specific files"""
    if not os.path.exists(folder_path):
        return None
        
    sha256_hash = hashlib.sha256()

    def should_include_file(filename):
        """Check if file should be included in hash calculation"""
        # Skip files starting with _ or .
        if filename.startswith('_') or filename.startswith('.'):
            return False
            
        # Skip files ending with .db or .log
        if filename.endswith('.db') or filename.endswith('.log'):
            return False
            
        return True

    for root, dirs, files in os.walk(folder_path):
        # Sort files for consistent hash across platforms
        for filename in sorted(files):
            if not should_include_file(filename):
                local_logging.debug(f"Skipping file: {filename}")
                continue
                
            filepath = os.path.join(root, filename)
            try:
                with open(filepath, 'rb') as f:
                    for byte_block in iter(lambda: f.read(4096), b''):
                        sha256_hash.update(byte_block)
            except (IOError, PermissionError) as e:
                local_logging.warning(f"Couldn't read file {filepath}: {e}")
                continue

    return sha256_hash.hexdigest()
