import os
import json
from unittest.suite import TestSuite
import subprocess
import unittest
from helper import *
import requests
from mechanism.reactions import *
from mechanism.species import *

s = requests.session()
s.cookies.set("sessionid", "testsessionid", domain="127.0.0.1")
base_dir = 'interactive'
example_base = 'interactive/dashboard/static/examples'


class UnitTestRunner(unittest.TestCase):
    def test_all_config_files(self):
        # look for all config files
        examples_path = os.path.join(base_dir, 'dashboard/static/examples')
        print("Test Case #1: check that all config files are present")

        # fetch all files in each examples directories
        example_1_path = os.path.join(examples_path, 'example_1')
        files1 = sorted(get_list_of_files(example_1_path))
        eg1 = '/example_1/camp_data/'
        ez = '/example_1/'
        expected_files_1 = sorted([example_base + eg1 + 'species.json',
                            example_base + eg1 + 'tolerance.json',
                            example_base + eg1 + 'reactions.json',
                            example_base + eg1 + 'config.json',
                            example_base + ez + 'my_config.json',
                            example_base + ez + 'MusicBox_1_60hPa.csv'])
        self.assertEqual(files1, expected_files_1)
        print("\t - example_1 files look good ✓")

        example_2_path = os.path.join(examples_path, 'example_2')
        files2 = sorted(get_list_of_files(example_2_path))
        eg2 = '/example_2/camp_data/'
        ez2 = '/example_2/'
        expected_files_2 = sorted([example_base + eg2 + 'species.json',
                            example_base + eg2 + 'tolerance.json',
                            example_base + eg2 + 'reactions.json',
                            example_base + eg2 + 'config.json',
                            example_base + ez2 + 'my_config.json',
                            example_base + ez2 + 'initial_reaction_rates.csv'])

        self.assertEqual(files2, expected_files_2)
        print("\t - example_2 files look good ✓")

        example_3_path = os.path.join(examples_path, 'example_3')
        files3 = sorted(get_list_of_files(example_3_path))
        eg3 = '/example_3/camp_data/'
        ez3 = '/example_3/'
        expected_files_3 = sorted([example_base + eg3 + 'species.json',
                            example_base + eg3 + 'tolerance.json',
                            example_base + eg3 + 'reactions.json',
                            example_base + eg3 + 'config.json',
                            example_base + ez3 + 'my_config.json',
                            example_base + ez3 + 'initial_reaction_rates.csv'])
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
        example_1_expected_checksum = "1979c4aeaa0fcd9f89b019276edd34d4"
        self.assertEqual(example_1_checksum, example_1_expected_checksum)
        print("\t - example_1 checksum good ✓")

        # get check sum from example_2
        example_2_path = os.path.join(examples_path, 'example_2')
        example_2_checksum = calculate_checksum(example_2_path)
        example_2_expected_checksum = "5a9b4fbb43c1778f78949b2cbd8da309"
        self.assertEqual(example_2_checksum, example_2_expected_checksum)
        print("\t - example_2 checksum good ✓")

        # get check sum from example_3
        example_3_path = os.path.join(examples_path, 'example_3')
        example_3_checksum = calculate_checksum(example_3_path)
        example_3_expected_checksum = "f25600931179b57fccdee625e2983d7b"
        self.assertEqual(example_3_checksum, example_3_expected_checksum)
        print("\t - example_3 checksum good ✓")

    def test_changed_species_config_file(self):
        # edit a config file and check that the checksum changes
        print("Test Case #3: change species file")
        # set output time step to 500 seconds in my_config.json

        # example_1 species location
        config_path = example_base + '/example_1/camp_data/species.json'
        species_to_remove = "N2"
        species_remove(species_to_remove, config_path)

        reac_path = example_base + '/example_1/camp_data/reactions.json'
        my_path = example_base + '/example_1/my_config.json'
        remove_reactions_with_species(species_to_remove, reac_path,
                                      my_path)
        example_1_expected_checksum = "b56eb7dcc51e29bb6dc71fb9caa076be"
        examples_path = example_base

        # get check sum from example_1
        example_1_path = os.path.join(examples_path, 'example_1')
        example_1_checksum = calculate_checksum(example_1_path)
        self.assertEqual(example_1_checksum, example_1_expected_checksum)
        print("\t - removed N2 ✓")

    def test_changed_reactions_config_file(self):
        print("Test Case #4: change reactions config file")
        # remove reaction @ index 0
        config_path = example_base + '/example_1/camp_data/reactions.json'
        reaction_remove(0, config_path)

        example_1_expected_checksum = "6f14589d8058644358dd26f764487716"
        examples_path = os.path.join(base_dir, 'dashboard/static/examples')

        # get check sum from example_1
        example_1_path = os.path.join(examples_path, 'example_1')
        example_1_checksum = calculate_checksum(example_1_path)

        self.assertEqual(example_1_checksum, example_1_expected_checksum)
        print("\t - removed first reaction ✓")

    def test_changed_conditions_file(self):
        print("Test Case #5: change conditions file")
        new_json = '{"chem_step.units":"min","output_step.units":"sec","simulation_length.units":"day","grid":"box","chemistry_time_step":"1","output_time_step":"500","simulation_length":"5"}'
        newOptions = json.loads(new_json)


# stop all processes (including running django server)
def stopAllProcesses():
    print("* stopping all processes")
    subprocess.run(["pkill", "python"])


# check if main
if __name__ == '__main__':
    # run tests
    # runner = UnitTestRunner()
    # runner.test_config_files_checksums()
    # stopAllProcesses()
    print("* running test cases")
    print("--------------------------------------------------")
    # unittest.main() # run   all tests
    runner = UnitTestRunner()
    runner.test_all_config_files()
    runner.test_config_files_checksums()
    runner.test_changed_species_config_file()
    runner.test_changed_reactions_config_file()
    # runner.test_changed_conditions_file()
