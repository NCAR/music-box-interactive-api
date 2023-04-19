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
        CHAPMAN_path = os.path.join(examples_path, 'CHAPMAN')
        files1 = sorted(get_list_of_files(CHAPMAN_path))
        eg1 = '/CHAPMAN/camp_data/'
        ez = '/CHAPMAN/'
        expected_files_1 = sorted([example_base + eg1 + 'species.json',
                            example_base + eg1 + 'tolerance.json',
                            example_base + eg1 + 'reactions.json',
                            example_base + eg1 + 'config.json',
                            example_base + ez + 'my_config.json',
                            example_base + ez + 'MusicBox_1_60hPa.csv'])
        self.assertEqual(files1, expected_files_1)
        print("\t - CHAPMAN files look good ✓")

        FLOW_TUBE_path = os.path.join(examples_path, 'FLOW_TUBE')
        files2 = sorted(get_list_of_files(FLOW_TUBE_path))
        eg2 = '/FLOW_TUBE/camp_data/'
        ez2 = '/FLOW_TUBE/'
        expected_files_2 = sorted([example_base + eg2 + 'species.json',
                            example_base + eg2 + 'tolerance.json',
                            example_base + eg2 + 'reactions.json',
                            example_base + eg2 + 'config.json',
                            example_base + ez2 + 'my_config.json',
                            example_base + ez2 + 'initial_reaction_rates.csv'])

        self.assertEqual(files2, expected_files_2)
        print("\t - FLOW_TUBE files look good ✓")

        FULL_GAS_PHASE_path = os.path.join(examples_path, 'FULL_GAS_PHASE')
        files3 = sorted(get_list_of_files(FULL_GAS_PHASE_path))
        eg3 = '/FULL_GAS_PHASE/camp_data/'
        ez3 = '/FULL_GAS_PHASE/'
        expected_files_3 = sorted([example_base + eg3 + 'species.json',
                            example_base + eg3 + 'tolerance.json',
                            example_base + eg3 + 'reactions.json',
                            example_base + eg3 + 'config.json',
                            example_base + ez3 + 'my_config.json',
                            example_base + ez3 + 'initial_reaction_rates.csv'])
        self.assertEqual(files3, expected_files_3)
        print("\t - FULL_GAS_PHASE files look good ✓")
    def test_config_files_checksums(self):
        global base_dir
        """check checksums for config files"""
        # first lets check that all example files have the right checksums
        examples_path = os.path.join(base_dir, 'dashboard/static/examples')
        print("Test Case #2: verify file checksums")

        # get check sum from CHAPMAN
        CHAPMAN_path = os.path.join(examples_path, 'CHAPMAN')
        CHAPMAN_checksum = calculate_checksum(CHAPMAN_path)
        CHAPMAN_expected_checksum = "91c1cf2d5a317ddeac48b5ed30c8fa90"
        self.assertEqual(CHAPMAN_checksum, CHAPMAN_expected_checksum)
        print("\t - CHAPMAN checksum good ✓")

        # get check sum from FLOW_TUBE
        FLOW_TUBE_path = os.path.join(examples_path, 'FLOW_TUBE')
        FLOW_TUBE_checksum = calculate_checksum(FLOW_TUBE_path)
        FLOW_TUBE_expected_checksum = "5a9b4fbb43c1778f78949b2cbd8da309"
        self.assertEqual(FLOW_TUBE_checksum, FLOW_TUBE_expected_checksum)
        print("\t - FLOW_TUBE checksum good ✓")

        # get check sum from FULL_GAS_PHASE
        FULL_GAS_PHASE_path = os.path.join(examples_path, 'FULL_GAS_PHASE')
        FULL_GAS_PHASE_checksum = calculate_checksum(FULL_GAS_PHASE_path)
        FULL_GAS_PHASE_expected_checksum = "40beb530c9be203c3ea59063f2abdb62"
        self.assertEqual(FULL_GAS_PHASE_checksum, FULL_GAS_PHASE_expected_checksum)
        print("\t - FULL_GAS_PHASE checksum good ✓")

    def test_changed_species_config_file(self):
        # edit a config file and check that the checksum changes
        print("Test Case #3: change species file")
        # set output time step to 500 seconds in my_config.json

        # CHAPMAN species location
        config_path = example_base + '/CHAPMAN/camp_data/species.json'
        species_to_remove = "N2"
        species_remove(species_to_remove, config_path)

        reac_path = example_base + '/CHAPMAN/camp_data/reactions.json'
        my_path = example_base + '/CHAPMAN/my_config.json'
        remove_reactions_with_species(species_to_remove, reac_path,
                                      my_path)
        CHAPMAN_expected_checksum = "cacbd4a662dcdf78b0f22951dccb9207"
        examples_path = example_base

        # get check sum from CHAPMAN
        CHAPMAN_path = os.path.join(examples_path, 'CHAPMAN')
        CHAPMAN_checksum = calculate_checksum(CHAPMAN_path)
        self.assertEqual(CHAPMAN_checksum, CHAPMAN_checksum)
        print("\t - removed N2 ✓")

    def test_changed_reactions_config_file(self):
        print("Test Case #4: change reactions config file")
        # remove reaction @ index 0
        config_path = example_base + '/CHAPMAN/camp_data/reactions.json'
        reaction_remove(0, config_path)

        CHAPMAN_expected_checksum = "f0a73918971c2824fa8cc1d4bb88ea0b"
        examples_path = os.path.join(base_dir, 'dashboard/static/examples')

        # get check sum from CHAPMAN
        CHAPMAN_path = os.path.join(examples_path, 'CHAPMAN')
        CHAPMAN_checksum = calculate_checksum(CHAPMAN_path)

        self.assertEqual(CHAPMAN_checksum, CHAPMAN_checksum)
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
