from dotenv import load_dotenv
from pathlib import Path
import os

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

class Env:
    API_KEY = os.getenv("CHATGPT_API")
