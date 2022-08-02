import os
import json
# from rest_framework import status
# from django.test import TestCase, Client
# from django.test import TransactionTestCase
# from django.test.runner import DiscoverRunner
from unittest.suite import TestSuite
import subprocess
import unittest
from helper import *
import requests
from mechanism.reactions import *
from mechanism.species import *

s = requests.session()
s.cookies.set("sessionid", "testsessionid", domain="127.0.0.1")
# initialize the APIClient app
# client = Client()
base_dir = 'interactive'



class UnitTestRunner(unittest.TestCase):


    def test_all_config_files(self):
        # look for all config files
        examples_path = os.path.join(base_dir, 'dashboard/static/examples')
        print("Test Case #1: check that all config files are present")

        # fetch all files in each examples directories
        example_1_path = os.path.join(examples_path, 'example_1')
        files1 = getListOfFiles(example_1_path)
        expected_files_1 = ['interactive/dashboard/static/examples/example_1/camp_data/species.json', 'interactive/dashboard/static/examples/example_1/camp_data/tolerance.json', 'interactive/dashboard/static/examples/example_1/camp_data/reactions.json', 'interactive/dashboard/static/examples/example_1/camp_data/config.json', 'interactive/dashboard/static/examples/example_1/my_config.json', 'interactive/dashboard/static/examples/example_1/MusicBox_1_60hPa.csv']
        self.assertEqual(files1, expected_files_1)
        print("\t - example_1 files look good ✓")

        example_2_path = os.path.join(examples_path, 'example_2')
        files2 = getListOfFiles(example_2_path)
        expected_files_2 = ['interactive/dashboard/static/examples/example_2/camp_data/species.json',
        'interactive/dashboard/static/examples/example_2/camp_data/tolerance.json',
        'interactive/dashboard/static/examples/example_2/camp_data/reactions.json',
        'interactive/dashboard/static/examples/example_2/camp_data/config.json',
        'interactive/dashboard/static/examples/example_2/my_config.json',
        'interactive/dashboard/static/examples/example_2/initial_reaction_rates.csv']

        self.assertEqual(files2, expected_files_2)
        print("\t - example_2 files look good ✓")

        example_3_path = os.path.join(examples_path, 'example_3')
        files3 = getListOfFiles(example_3_path)
        expected_files_3 = ['interactive/dashboard/static/examples/example_3/camp_data/species.json',
        'interactive/dashboard/static/examples/example_3/camp_data/tolerance.json',
        'interactive/dashboard/static/examples/example_3/camp_data/reactions.json',
        'interactive/dashboard/static/examples/example_3/camp_data/config.json',
        'interactive/dashboard/static/examples/example_3/my_config.json',
        'interactive/dashboard/static/examples/example_3/initial_reaction_rates.csv']
        self.assertEqual(files3, expected_files_3)
        print("\t - example_3 files look good ✓")


    def test_config_files_checksums(self):
        global base_dir
        """check checksums for config files"""
        # first lets check that all example files have the right checksums
        
        examples_path = os.path.join(base_dir, 'dashboard/static/examples')
        print("Test Case #2: verify file checksums")

        # get check sum from example_1
        example_1_path = os.path.join(examples_path, 'example_1')
        example_1_checksum = calculate_checksum(example_1_path)
        example_1_expected_checksum = "b56eb7dcc51e29bb6dc71fb9caa076be" # b3f3a80960f3826896d6f1f116e5f604
        self.assertEqual(example_1_checksum, example_1_expected_checksum)
        print("\t - example_1 checksum good ✓")

        # get check sum from example_2
        example_2_path = os.path.join(examples_path, 'example_2')
        example_2_checksum = calculate_checksum(example_2_path)
        example_2_expected_checksum = "e0b89901696a3779ad6b910e24eaeb4c" # e659ad1a567c09dc2c16e32a8f475748
        self.assertEqual(example_2_checksum, example_2_expected_checksum)
        print("\t - example_2 checksum good ✓")

        # get check sum from example_3
        example_3_path = os.path.join(examples_path, 'example_3')
        example_3_checksum = calculate_checksum(example_3_path)
        example_3_expected_checksum = "f25600931179b57fccdee625e2983d7b" # 47ae9f6212cddb7a079119a57aceac9b
        self.assertEqual(example_3_checksum, example_3_expected_checksum)
        print("\t - example_3 checksum good ✓")

    def test_changed_species_config_file(self):
        # edit a config file and check that the checksum changes
        print("Test Case #3: check that checksum changes when species config file changes")
        # set output time step to 500 seconds in my_config.json for first example

        # example_1 species location
        config_path = os.path.join(base_dir, 'dashboard/static/examples/example_1/camp_data/species.json')
        species_to_remove = "N2"
        species_remove(species_to_remove, config_path)

        reac_path = os.path.join(base_dir, 'dashboard/static/examples/example_1/camp_data/reactions.json')
        my_path = os.path.join(base_dir, 'dashboard/static/examples/example_1/my_config.json')
        remove_reactions_with_species(species_to_remove, reac_path,
                                        my_path)
        example_1_expected_checksum = "17158dd0c38c409e58fa8020eb049381"
        examples_path = os.path.join(base_dir, 'dashboard/static/examples')

        # get check sum from example_1
        example_1_path = os.path.join(examples_path, 'example_1')
        example_1_checksum = calculate_checksum(example_1_path)
        self.assertEqual(example_1_checksum, example_1_expected_checksum)
        print("\t - time step changed to 500 seconds ✓")
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
