import os
import json
from rest_framework import status
from django.test import TestCase, Client
from django.test import TransactionTestCase
from django.test.runner import DiscoverRunner
from unittest.suite import TestSuite
import subprocess
import unittest
from django.conf import settings
from helper import *

# initialize the APIClient app
client = Client()

class UnitTestRunner(unittest.TestCase):

    def test_config_files_checksums(self):
        """check checksums for config files"""
        # first lets check that all example files have the right checksums
        
        examples_path = os.path.join(
            settings.BASE_DIR, 'dashboard/static/examples')
        print("* testing config files checksums in: %s" % examples_path)
        # get check sum from example_1
        example_1_path = os.path.join(examples_path, 'example_1')
        example_1_checksum = calculate_checksum(example_1_path)
        example_1_expected_checksum = "b3f3a80960f3826896d6f1f116e5f604"
        self.assertEqual(example_1_checksum, example_1_expected_checksum)
        print("|_ example_1 checksum good ✓")
        # get check sum from example_2
        example_2_path = os.path.join(examples_path, 'example_2')
        example_2_checksum = calculate_checksum(example_2_path)
        example_2_expected_checksum = "e659ad1a567c09dc2c16e32a8f475748"
        self.assertEqual(example_2_checksum, example_2_expected_checksum)
        print("|_ example_2 checksum good ✓")
        # get check sum from example_3
        example_3_path = os.path.join(examples_path, 'example_3')
        example_3_checksum = calculate_checksum(example_3_path)
        example_3_expected_checksum = "47ae9f6212cddb7a079119a57aceac9b"
        self.assertEqual(example_3_checksum, example_3_expected_checksum)
        print("|_ example_3 checksum good ✓")  
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
    print("* running test cases")
    print("----------------------------------------------------------------------")
    unittest.main() # run   all tests
