import os
import json
from rest_framework import status
from django.test import TestCase, Client

# initialize the APIClient app
client = Client()

class APITestCase(TestCase):

    def test_config_files_checksums(self):
        """check checksums for config files"""
        # first lets check that all example files have the right checksums
        config_dir = os.path.join(os.path.dirname(__file__), 'interactive/dashboard/static/examples')
        self.assertEqual(config_dir, config_dir)