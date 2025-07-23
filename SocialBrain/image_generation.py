import os
import openai
from dotenv import load_dotenv

# Load your API key
load_dotenv()
# openai.api_key = os.getenv("OPENAI_API_KEY")

from openai import OpenAI
client = OpenAI()

def generate_image(prompt: str, size: str = "1024x1024", quality: str = "standard", n: int = 1):
    
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality=quality,
        n=n,
    )

    return response.data[0].url,response.data[0].b64_json