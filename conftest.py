import sys
from pathlib import Path

# Add the project root to Python's path so tests can import from src/
sys.path.insert(0, str(Path(__file__).parent))