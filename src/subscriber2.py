from message_broker import MessageBroker
import json

class AnalyticsService:
    def __init__(self):
        self.broker = MessageBroker()
        self.setup_subscriptions()
    
    def setup_subscriptions(self):
        self.broker.subscribe("data_processed", self.handle_processed_data)
    
    def handle_processed_data(self, message):
        data = json.loads(message['data'])
        print(f"Analytics: Recording processed data: {data}")
        # Here you could store analytics data in a database
    
    def start(self):
        print("Analytics service started...")
        self.broker.start_listening()

if __name__ == "__main__":
    service = AnalyticsService()
    service.start() 