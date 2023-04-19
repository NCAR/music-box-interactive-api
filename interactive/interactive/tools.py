import os
import json
base_dir = '/music-box-interactive/interactive'
try:
    from django.conf import settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'interactive.settings')
    base_dir = settings.BASE_DIR
except ModuleNotFoundError:
    # Error handling
    pass
from ..shared.unit_dict import *
from ..shared.conversion_dict import *
from ..shared.converter_class import Unit

