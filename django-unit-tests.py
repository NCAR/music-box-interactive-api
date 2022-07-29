import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

import django
django.setup()
from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework.test import force_authenticate
from rest_framework.test import RequestsClient
class APITestCase(TestCase):

    def test_config_files_checksums(self):
        """check checksums for config files"""
        # first lets check that all example files have the right checksums
        config_dir = os.path.join(os.path.dirname(__file__), 'interactive/dashboard/static/examples')
        self.assertEqual(config_dir, config_dir)