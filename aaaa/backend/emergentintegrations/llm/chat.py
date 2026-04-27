"""Stub chat module"""
from typing import Optional, List
from datetime import datetime

class UserMessage:
    def __init__(self, text: str):
        self.text = text

class LlmChat:
    def __init__(self, api_key: str = None, session_id: str = None, system_message: str = None):
        self.api_key = api_key
        self.session_id = session_id
        self.system_message = system_message
        self.model = None
    
    def with_model(self, provider: str, model_name: str):
        self.model = f"{provider}:{model_name}"
        return self
    
    async def send_message(self, message):
        # Return mock response
        return '{"opportunities": []}'
