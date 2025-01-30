# Lightweight Messaging Service Example

This project demonstrates a simple pub/sub messaging system using Redis.

## Setup

1. Install Redis on your system
2. Install Python dependencies:
   ```bash
   sh dev_setup.sh
   ```

## Running the Application

1. Start Redis server
2. Run subscribers in separate terminals:
   ```
   python src/monitor_server.py
   python src/monitor_folder.py
   python src/monitor_repo.py
   ```

## Components

- `message_broker.py`: Core messaging functionality using Redis
- `monitor_folder.py`: Monitor folder for setup
- `monitor_repo.py`: Monitor repo for setup
- `monitor_server.py`: Monitor server for setup