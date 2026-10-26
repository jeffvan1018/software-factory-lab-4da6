import os
from dotenv import load_dotenv

load_dotenv()

BUCKET_NAME = os.getenv("FACTORY_BUCKET")
MODEL_NAME = os.getenv("GOOGLE_CLOUD_MODEL", "gemini-3.8-flash")

if not BUCKET_NAME:
    raise ValueError("FACTORY_BUCKET must be set.")
