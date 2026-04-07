import os
os.environ["DEEPSEEK_API_KEY"] = "dummy_key"
from src.main import SocraticTutorApp
try:
    app = SocraticTutorApp()
    print("App loaded successfully.")
except Exception as e:
    print(f"Error loading app: {e}")
