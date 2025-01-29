from message_broker import MessageBroker
import json

class NotificationService:
    def __init__(self):
        self.broker = MessageBroker()
        self.setup_subscriptions()
    
    def setup_subscriptions(self):
        self.broker.subscribe("Git Clone ok", self.handle_processed_data)
    
    def handle_processed_data(self, message):
        data = json.loads(message['data'])
        print(f"Notification: Data processing completed: {data}")
    
    def start(self):
        print("Notification service started...")
        self.broker.start_listening()

if __name__ == "__main__":
    service = NotificationService()
    service.start() 