import os
import sys
from pathlib import Path

# Automatically resolve base directory (assumes this file is at <project_root>/<project_name>/wsgi.py)
current_file = Path(__file__).resolve()
project_name = current_file.parent.name
project_root = current_file.parent.parent             

# Add project root and project name (inner folder) to sys.path
sys.path.insert(0, str(project_root))
sys.path.insert(1, str(project_root / project_name))

# Set the default settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'{project_name}.settings')

# Django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
