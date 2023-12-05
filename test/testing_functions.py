from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time
import json
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select


# utility functions for building tests

def set_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_prefs = {}
    chrome_options.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    return chrome_options


def create_browser():
    browser = webdriver.Chrome(options=set_chrome_options())
    return browser


def get_page(browser, page):
    url = 'http://localhost:8000/' + page
    browser.get(url)
    time.sleep(.5)


with open('xpaths.json') as f:
    xpaths = json.load(f)


def click_on(browser, pathlist):
    xpath = xpaths
    for i in pathlist:
        xpath = xpath[i]
    browser.find_element_by_xpath(xpath).send_keys(Keys.NULL)
    browser.find_element_by_xpath(xpath).click()
    time.sleep(.5)


# clears input and fills in inputString
def input_keys(browser, pathlist, inputString):
    xpath = xpaths
    for i in pathlist:
        xpath = xpath[i]
    browser.find_element_by_xpath(xpath).clear()
    browser.find_element_by_xpath(xpath).send_keys(inputString)
    time.sleep(0.5)


# chooses from select field
def dropdown_select(browser, pathlist, selection):
    xpath = xpaths
    for i in pathlist:
        xpath = xpath[i]
    selectfield = Select(browser.find_element_by_xpath(xpath))
    selectfield.select_by_visible_text(selection)
    time.sleep(0.5)
