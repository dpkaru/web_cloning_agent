'''import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")'''

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Primary model from your .env file
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Fallback models arranged in order of stability to route traffic dynamically if primary fails
FALLBACK_MODELS = [
    "gemini-2.0-flash", 
    "gemini-1.5-flash"
]
