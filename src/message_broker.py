import redis
from typing import Callable
import json


class MessageBroker:
    def __init__(self, host='localhost', port=6379):
        self.redis_client = redis.Redis(host=host, port=port)
        self.pubsub = self.redis_client.pubsub()
    
    def publish(self, channel: str, message: dict):
        """Publish a message to a specific channel"""
        message_str = json.dumps(message)
        self.redis_client.publish(channel, message_str)
    
    def subscribe(self, channel: str, callback: Callable):
        """Subscribe to a channel with a callback function"""
        self.pubsub.subscribe(**{channel: callback})
    
    def start_listening(self):
        """Start listening for messages"""
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                # Get the channel and callback
                channel = message['channel'].decode('utf-8')
                # Execute the callback with the message
                self.pubsub.patterns[channel](message)