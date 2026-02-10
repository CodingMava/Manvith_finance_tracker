import sys
import os

print(f"Current working directory: {os.getcwd()}")
abs_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(abs_path)
print(f"Added to path: {abs_path}")
print("sys.path:")
for p in sys.path:
    print(p)

try:
    import core
    print(f"Successfully imported core: {core}")
    print(f"core file: {core.__file__}")
except ImportError as e:
    print(f"Failed to import core: {e}")

try:
    from core import settings
    print("Successfully imported core.settings")
except ImportError as e:
    print(f"Failed to import core.settings: {e}")
