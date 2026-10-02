import sys
from pathlib import Path

# let tests import the modules in the project folder
sys.path.insert(0, str(Path(__file__).parent.parent))
