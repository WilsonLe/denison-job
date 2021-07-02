import os
import sys
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.by import By
load_dotenv()


class WebDriver():
    def __init__(self):
        self.options = Options()
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        if os.getenv("PYTHON_ENV") == "production":
            self.options.add_argument('--headless')
        self.driver = None

    def handle_exception(self, ex):
        """handle exceptions with selenium

        Args:
            ex (Exception): exceptions raised by selenium
        """
        print(ex)

    def start(self):
        """start web driver application
        """
        try:
            self.driver = webdriver.Chrome(options=self.options)
        except Exception as ex:
            print(ex)

    def stop(self):
        """stop web driver application
        """
        if self.driver != None:
            self.driver.close()
        else:
            print('Driver has not started')

    def go_to(self, url):
        """Go to the specified URL

        Args:
            url (string): input url to go to. Should starts with https://
        """
        # make sure url starts with https://
        if not url.startswith('https://'):
            url = 'https://' + url

        try:
            self.driver.get(url)
        except Exception as ex:
            self.handle_exception(ex)

    def query_selector(self, selector):
        """query for an element

        Returns:
            [selenium.webdriver.remote.webelement.WebElement]: array of
            queried elements if selector is not by ID or XPATH
            selenium.webdriver.remote.webelement.WebElement: one element if
            selector is ID or XPATH
            None: if no element exist
        """
        try:
            elements = self.driver.find_elements_by_css_selector(selector)
            if selector.startswith('#') or selector.startswith('/'):
                if len(elements) > 0:
                    return elements[0]
                else:
                    return None
            else:
                return elements
        except Exception as ex:
            self.handle_exception(ex)

    def wait_for(self, selector, timeout=10):
        """wait for element with input selector to present

        Args:
            selector (string): css selector of element to wait for
            timeout (int, optional): maximum wait time. Defaults to 10.
        """
        try:
            element_present = EC.presence_of_element_located(
                (By.CSS_SELECTOR, selector))
            wait(
                self.driver, timeout).until(element_present)
        except Exception as ex:
            self.handle_exception(ex)

    def sleep(self, time):
        """implicitly wait for specified amount of time

        Args:
            time (int): number of seconds to wait
        """
        self.driver.implicitly_wait(time)

    def wait_for_and_switch_to_iframe(self, selector, timeout=60):
        """wait for iframe and switch to it

        Args:
            selector (string): css selector of element to wait for
            timeout (int, optional): [description]. Defaults to 60.
        """
        try:
            iframe_present = EC.frame_to_be_available_and_switch_to_it(
                selector)
            wait(
                self.driver, timeout).until(iframe_present)
        except Exception as ex:
            self.handle_exception(ex)

    def switch_default(self):
        """switch driver back to default, main content
        """
        self.driver.switch_to.default_content()
