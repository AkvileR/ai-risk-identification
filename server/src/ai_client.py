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

# Maybe prompt can be the same with only a couple of variables?
# If so put prompt builder here as well
def query_gemini(prompt: str):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return None