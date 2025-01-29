from message_broker import MessageBroker
import time

class DataProcessor:
    def __init__(self):
        self.broker = MessageBroker()
    
    def process_data(self, data: dict):
        # Simulate some processing
        print(f"Processing data: {data}")
        time.sleep(2)  # Simulate work
        
        # After processing, publish the result
        result = {
            "status": "completed",
            "processed_data": data,
            "timestamp": time.time()
        }
        self.broker.publish("data_processed", result)

if __name__ == "__main__":
    processor = DataProcessor()
    test_data = {"id": 0, "value": "test 0"}
    processor.process_data(test_data) 