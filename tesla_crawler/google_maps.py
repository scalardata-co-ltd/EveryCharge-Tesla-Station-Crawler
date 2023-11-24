from typing import Optional, Dict, Optional
import time

from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException


class GoogleMapCrawlerForDestinationCharger:
    base_url = 'https://www.google.com/maps'
    driver: Optional[WebDriver] = None

    def __init__(self):
        self.driver = None

    def generate_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--window-size-1920,1080')
        options.add_experimental_option('detach', True)

        options.add_argument('--no-sandbox')
        options.add_argument('--headless')

        self.driver = webdriver.Chrome(
            executable_path=ChromeDriverManager().install(),
            options=options)

    def open_driver(self):
        if not self.driver:
            self.generate_driver()
        self.driver.get(self.base_url)
        self.driver.implicitly_wait(3)

    def close_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def __del__(self):
        self.close_driver()

    def action_search_charger(self, address: str):
        input_form = self.driver.find_element(By.ID, 'gs_lc50') \
                                .find_element(By.TAG_NAME, 'input')
        input_form.clear()
        input_form.send_keys('Tesla Destination Charger, ' + address)
        input_form.send_keys(Keys.ENTER)
        time.sleep(3)

    def is_tesla(self) -> bool:
        elements = self.driver.find_elements(By.CLASS_NAME, 'DUwDvf')
        if not elements:
            return False
        location_name = elements[0].text
        return location_name == 'Tesla Destination Charger'

    def get_max_kwh(self) -> Optional[int]:
        try:
            raw_max_kwh = self.driver.find_element(By.CLASS_NAME, 'NiVgee') \
                                    .find_element(By.TAG_NAME, 'span') \
                                    .find_element(By.TAG_NAME, 'span').text
        except NoSuchElementException:
            return None
        return int(raw_max_kwh[2:-2])

    def get_charger_count(self) -> Optional[int]:
        try:
            raw_charger_count = self.driver.find_element(By.CLASS_NAME, 'lmLZWe ') \
                                    .find_element(By.TAG_NAME, 'span') \
                                    .find_element(By.TAG_NAME, 'span').text
        except NoSuchElementException:
            return None
        return int(raw_charger_count)

    def get_charger_data(self) -> Optional[Dict]:
        max_kwh, charger_count = self.get_max_kwh(), self.get_charger_count()
        if max_kwh is None or charger_count is None:
            return None
        return {
            'type': 'destination',
            'max_kwh': max_kwh,
            'charger_count': charger_count
        }

    def find_tesla_destinaiton_charger_data(self, address: str) -> Optional[Dict]:
        self.action_search_charger(address)
        if not self.is_tesla():
            return None
        return self.get_charger_data()
