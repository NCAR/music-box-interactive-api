from django.conf import settings
from django.http import Http404

import logging
import os

logger = logging.getLogger(__name__)

def load_example(example):
  conditions = {}
  mechanism = {}

  example_path = os.path.join(
      settings.BASE_DIR, 'dashboard/static/examples', example)

  files = [os.path.join(dp, f) for dp, _, fn in os.walk(example_path) for f in fn]
  logger.info(files)
  if not files:
      raise Http404("No files in example folder")
    
  return conditions, mechanism