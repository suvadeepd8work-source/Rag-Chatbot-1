# Vercel entry point (api/index.py)
import sys
import os

# Add the project root to the path so we can import from Phases
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the FastAPI app from Phase 4
from Phase_4_Backend_API.main import app

# Vercel expects the app to be named 'app'
# Since we imported it as 'app', it should work automatically.
