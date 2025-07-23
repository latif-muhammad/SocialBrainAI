import requests
import json
from generate_post import get_user_input


user_input , num_posts, tone = get_user_input()

payload = {
    "prompt": user_input,
    "num_posts": num_posts,
    "tone": tone
}

API_URL = "http://localhost:8000/generate_post"  # Replace with your API URL

response = requests.post(API_URL, json=payload)
if response.status_code == 200:
    data = response.json()
    print("Generated Post:", data["post"])