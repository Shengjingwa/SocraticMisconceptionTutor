import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

os.environ["DEEPSEEK_API_KEY"] = "dummy_key"
from main import SocraticTutorApp
try:
    app = SocraticTutorApp()
    print("App loaded successfully.")
except Exception as e:
    print(f"Error loading app: {e}")
