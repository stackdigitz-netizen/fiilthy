"""Stub image generation module"""

class OpenAIImageGeneration:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
    
    async def generate_image(self, prompt: str, size: str = "1024x1024"):
        return "https://via.placeholder.com/1024x1024"
