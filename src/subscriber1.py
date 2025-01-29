from message_broker import MessageBroker
import json

class NotificationService:
    def __init__(self):
        self.broker = MessageBroker()
        self.setup_subscriptions()
    
    def setup_subscriptions(self):
        self.broker.subscribe("repo_ready", self.handle_processed_data)
    
    def handle_processed_data(self, message):
        try:
            data = json.loads(message['data'].decode('utf-8'))
            print(f"Notification: Received message: {data}")
        except Exception as e:
            print(f"Error processing message: {e}")
    
    def start(self):
        print("Notification service started...")
        self.broker.start_listening()

if __name__ == "__main__":
    service = NotificationService()
    service.start() 