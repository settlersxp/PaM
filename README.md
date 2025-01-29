# Lightweight Messaging Service Example

This project demonstrates a simple pub/sub messaging system using Redis.

## Setup

1. Install Redis on your system
2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

1. Start Redis server
2. Run subscribers in separate terminals:
   ```
   python src/subscriber1.py
   python src/subscriber2.py
   ```
3. Run the publisher:
   ```
   python src/publisher.py
   ```

## Components

- `message_broker.py`: Core messaging functionality using Redis
- `publisher.py`: Example service that processes data and publishes results
- `subscriber1.py`: Notification service that reacts to processed data
- `subscriber2.py`: Analytics service that records processed data
