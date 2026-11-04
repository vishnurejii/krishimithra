"""
WSGI config for KrishiMitra AI.
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
