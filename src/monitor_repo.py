import os
import time
from git import Repo, GitCommandError
import requests
import logging
import redis
import json

from deployment_utils import (
    register_logger,
    CLONED_PROJECT_PATH
)
import sys
from message_broker import MessageBroker

# Setup logging
logger = register_logger('monitor_repo')

REPO_URL = "git@github.com:settlersxp/SimpleTradingFramework.git"
CHECK_INTERVAL = 300  # 5 minutes in seconds


class RepositoryMonitor:
    def __init__(self):
        self.broker = MessageBroker()
        
    def clone_repo(self):
        """Clone the repository if it doesn't exist"""
        if not os.path.exists(CLONED_PROJECT_PATH):
            logging.info(f"Cloning repository from {REPO_URL}")
            try:
                Repo.clone_from(REPO_URL, CLONED_PROJECT_PATH)
                logging.info("Repository cloned successfully")
                self._publish_status("repo_ready", True)
            except GitCommandError as e:
                logging.error(f"Failed to clone repository: {e}")
                self._publish_status("repo_ready", False, str(e))
                sys.exit(1)

    def pull_repo(self):
        """Pull changes from the repository"""
        try:
            repo = Repo(CLONED_PROJECT_PATH)
            repo.git.pull()
            self._publish_status("repo_ready", True)
        except GitCommandError as e:
            logging.error(f"Failed to pull repository: {e}")
            self._publish_status("repo_ready", False, str(e))

    def stop_server(self):
        """Stop the server"""
        try:
            response = requests.get("http://localhost:3200/shutdown")
            logging.info(f"Server app termination response: {response}")
            if response.status_code == 200:
                logging.info("Server app terminated successfully")
                self._publish_status("server_terminated", True)
            else:
                logging.info("Server app not running")
                self._publish_status("server_terminated", True)
            return True
        except requests.exceptions.ConnectionError:
            logging.info("Server app not running")
            self._publish_status("server_terminated", True)
            return False

    def check_for_updates(self):
        """Check for updates in the repository"""
        try:
            repo = Repo(CLONED_PROJECT_PATH)
            current_hash = repo.head.commit.hexsha

            # Fetch updates from remote
            origin = repo.remotes.origin
            origin.fetch()

            # Get the hash of the remote master branch
            remote_hash = origin.refs.master.commit.hexsha

            if current_hash != remote_hash:
                termination_status = self.stop_server()

                if termination_status:
                    logging.info("Server app terminated successfully")
                    
                    self.pull_repo()
                return True

        except GitCommandError as e:
            logging.error(f"Git operation failed: {e}")
            self._publish_status("git_operation", False, str(e))
            return False

    def _publish_status(self, event_type: str, success: bool, error_msg: str = None):
        """Publish repository status updates"""
        message = {
            "event": event_type,
            "success": success,
            "timestamp": time.time(),
            "error": error_msg
        }
        self.broker.publish(event_type, message)

    def run(self):
        """Main monitoring loop"""
        # Initial setup
        self.clone_repo()

        logging.info("Starting repository monitor")
        while True:
            try:
                if self.check_for_updates():
                    logging.info("Updates applied successfully")
                else:
                    logging.info("No updates found")

                # Wait for next check
                time.sleep(CHECK_INTERVAL)

            except KeyboardInterrupt:
                logging.info("Monitor stopped by user")
                self._publish_status("monitor_stopped", True)
                break
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
                self._publish_status("unexpected_error", False, str(e))
                time.sleep(CHECK_INTERVAL)


def main():
    monitor = RepositoryMonitor()
    monitor.run()


if __name__ == "__main__":
    main()
