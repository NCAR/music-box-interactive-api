from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time
import json
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from testing_functions import *

# this contains the tests


def change_conditions(browser):
    print("Starting test")
    print("")
# get example 1
    try:
        get_page(browser, 'getting_started')
        click_on(browser, ['getting started', 'select example'])
        click_on(browser, ['getting started', 'example 1'])
        print('...  example 1 loaded succesfully     ...')
    except BaseException:
        print("failed to select example 1")

# change general conditions
    try:
        get_page(browser, 'conditions/options')
        input_keys(
            browser, [
                'conditions', 'general', 'chemistry time step'], '2')
        input_keys(
            browser, [
                'conditions', 'general', 'output time step'], '201')
        input_keys(browser, ['conditions', 'general', 'simulation time'], '4')
        browser.find_element_by_id("optionsSave").submit()
        print('...  general conditions changed       ...')
    except BaseException:
        print('failed to change model options')

# change species
    try:
        get_page(browser, 'conditions/initial')
        # remove O3
        get_page(browser, 'conditions/species/remove?species=Species%206.Units')
        get_page(browser, 'conditions/initial')

        time.sleep(0.5)
        # add O3 again
        click_on(browser, ['conditions', 'initial', 'add species'])
        dropdown_select(
            browser, [
                'conditions', 'initial', 'species 6 name'], "O3")
        input_keys(browser, ['conditions', 'initial',
                   'species 6 initial value'], "101")
        dropdown_select(
            browser, [
                'conditions', 'initial', 'species 6 units'], "mol cm-3")

        browser.find_element_by_id("speciesSave").submit()
        print('...  species changed                  ...')
    except BaseException:
        print('failed to change species')


# change temp and pressure
    try:
        get_page(browser, 'conditions/initial')
        input_keys(browser, ['conditions', 'initial', 'temperature'], "101")
        input_keys(browser, ['conditions', 'initial', 'pressure'], "10101")
        dropdown_select(
            browser, [
                'conditions', 'initial', 'temperature units'], "F")
        dropdown_select(
            browser, [
                'conditions', 'initial', 'pressure units'], "mbar")
        browser.find_element_by_id("initialsSave").submit()

        print('...  initial conditions changed       ...')
    except BaseException:
        print('failed to change initial temp and pressure')

# run model

    try:
        click_on(browser, ['home', 'run model'])
        print('...  model run                        ...')
    except BaseException:
        print('failed to run model')
