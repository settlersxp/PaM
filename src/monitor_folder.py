import venv
import logging
import time
import pip
import os
from deployment_utils import (
    register_logger,
    ENV_PATH_OF_CLONED_PROJECT,
    CLONED_PROJECT_PATH
)
from message_broker import MessageBroker
import json


# Setup logging
logger = register_logger('monitor_folder')


class SetupHandler:
    def __init__(self):
        self.broker = MessageBroker()
        self.setup_subscriptions()

    def setup_subscriptions(self):
        """Subscribe to repo_ready messages"""
        self.broker.subscribe("repo_ready", self.handle_repo_ready)

    def handle_repo_ready(self, message):
        """Handle repo_ready messages"""
        try:
            data = json.loads(message['data'])
            if data.get('success', False):
                logging.info("Repository is ready, running setup scripts")
                self.run_setup_scripts()
            else:
                logging.error(f"Repository setup failed: {data.get('error')}")
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse message: {e}")

    def run_setup_scripts(self):
        env_builder = venv.EnvBuilder(
            system_site_packages=False,
            clear=True,
            symlinks=True,
            upgrade=True,
            with_pip=True
        )
        env_builder.create(ENV_PATH_OF_CLONED_PROJECT)
        pip.main(['install', '-r', os.path.join(CLONED_PROJECT_PATH, 'requirements.txt')])

        self.publish_setup_status(True)
        
    def publish_setup_status(self, success: bool, error_msg: str = None):
        """Publish setup completion status"""
        message = {
            "success": success,
            "timestamp": time.time(),
            "error": error_msg
        }
        self.broker.publish("setup_ready", message)

    def start(self):
        """Start listening for messages"""
        logging.info("Setup handler started...")
        self.broker.start_listening()


def main():
    handler = SetupHandler()
    try:
        handler.start()
    except KeyboardInterrupt:
        logging.info("Setup handler stopped by user")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
