import os
from dotenv import load_dotenv

load_dotenv()

BUCKET_NAME = os.getenv("FACTORY_BUCKET")
WORKSPACE_HOME = os.getenv("WORKSPACE_HOME", "/tmp")
MODEL_NAME = os.getenv("GOOGLE_CLOUD_MODEL", "gemini-3.8-flash")

if not BUCKET_NAME:
    raise ValueError("FACTORY_BUCKET must be set.")
