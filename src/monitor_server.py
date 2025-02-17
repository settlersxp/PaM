import logging
import os
import sys
from message_broker import MessageBroker
import json
from deployment_utils import (
    register_logger,
    ENV_PATH_OF_CLONED_PROJECT,
    CLONED_PROJECT_PATH
)
import time
from multiprocessing import Process


# Setup logging
logger = register_logger('monitor_server')


class MonitorServer:
    def __init__(self):
        self.broker = MessageBroker()
        self.setup_subscriptions()

    def setup_subscriptions(self):
        """Subscribe to setup_ready messages"""
        self.broker.subscribe("setup_ready", self.handle_setup_ready)

    def handle_setup_ready(self, message):
        """Handle setup_ready messages"""
        try:
            data = json.loads(message['data'].decode('utf-8'))
            if data.get('success', False):
                logging.info("Setup completed successfully, running server")
                self.run_server()
            else:
                logging.error(f"Setup failed: {data.get('error')}")
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse message: {e}")

    def run_server(self):
        """Start server"""
        try:
            # Add the project path to sys.path so we can import the app
            if CLONED_PROJECT_PATH not in sys.path:
                sys.path.append(CLONED_PROJECT_PATH)

            # Add the venv site-packages to sys.path
            if os.name == 'nt':  # Windows
                site_packages = os.path.join(ENV_PATH_OF_CLONED_PROJECT, 'Lib', 'site-packages')
            else:  # Unix/Linux
                site_packages = os.path.join(ENV_PATH_OF_CLONED_PROJECT, 'lib', 
                                           f'python{sys.version_info.major}.{sys.version_info.minor}',
                                           'site-packages')
            if site_packages not in sys.path:
                sys.path.append(site_packages)
            
            # Import the Flask app
            sys.path.insert(0, CLONED_PROJECT_PATH)
            from run import FlaskApp

            # Create Flask app instance
            flask_app = FlaskApp()

            # Create and start Flask server in a separate process
            server_process = Process(target=flask_app.run)
            server_process.start()
            logging.info("Flask server started in separate process")

            # Publish success status
            self.publish_migration_status(True)

        except Exception as e:
            logging.error(f"Migration failed: {e}")
            self.publish_migration_status(False, str(e))

    def publish_migration_status(self, success: bool, error_msg: str = None):
        """Publish server completion status"""
        message = {
            "success": success,
            "timestamp": time.time(),
            "error": error_msg
        }
        self.broker.publish("server_ready", message)

    def start(self):
        """Start listening for messages"""
        logging.info("Server handler started...")
        self.broker.start_listening()


def main():
    handler = MonitorServer()
    try:
        handler.start()
    except KeyboardInterrupt:
        logging.info("Server handler stopped by user")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
