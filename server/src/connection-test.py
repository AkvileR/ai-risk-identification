"""
import os
from google import genai
from google.genai.types import HttpOptions
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(
    vertexai=True,                         
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location="us-central1",
    http_options=HttpOptions(api_version="v1")
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="How does AI work?",
)
print(response.text)
"""
