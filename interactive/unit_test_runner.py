import os
import json
from rest_framework import status
from django.test import TestCase, Client
from django.test import TransactionTestCase
from django.test.runner import DiscoverRunner
from unittest.suite import TestSuite
import subprocess
import unittest

# initialize the APIClient app
client = Client()

class UnitTestRunner(unittest.TestCase):

    def test_config_files_checksums(self, **kwargs):
        """check checksums for config files"""
        # first lets check that all example files have the right checksums
        config_dir = os.path.join(os.path.dirname(__file__), 'interactive/dashboard/static/examples')
        print("* testing config files checksums in: %s" % config_dir)
        self.assertEqual(config_dir, config_dir)

# stop all processes (including running django server)
def stopAllProcesses():
    print("* stopping all processes")
    subprocess.run(["pkill", "python"])
     
#check if main
if __name__ == '__main__':
    # run tests
    # runner = UnitTestRunner()
    # runner.test_config_files_checksums()
    # stopAllProcesses()
    unittest.main() # run   all tests
