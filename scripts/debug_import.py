import sys
import os
import django
from django.conf import settings

# Add current directory to path like manage.py does
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print(f"Current Directory: {os.getcwd()}")
print("Sys Path:")
for p in sys.path:
    print(f"  {p}")

try:
    import finance
    print(f"✅ Imported finance from: {finance.__file__}")
    try:
        from finance import DictTemplateLoader
        print("✅ Found DictTemplateLoader in finance")
    except ImportError as e:
        print(f"❌ Failed to import DictTemplateLoader from finance: {e}")
    except AttributeError as e:
        print(f"❌ Failed to find DictTemplateLoader attribute in finance: {e}")
except ImportError:
    print("❌ Could not import 'finance' module")

try:
    import core.template_loader
    print(f"✅ Imported core.template_loader from: {core.template_loader.__file__}")
except ImportError as e:
    print(f"❌ Could not import core.template_loader: {e}")

# Check settings content manually
try:
    import core.settings
    print(f"✅ Imported core.settings")
    if hasattr(core.settings, 'TEMPLATES'):
        print(f"TEMPLATES config: {core.settings.TEMPLATES}")
    else:
        print("❌ TEMPLATES not found in settings")
except ImportError as e:
    print(f"❌ Could not import core.settings: {e}")
