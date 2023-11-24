import time
from typing import Tuple, Optional

from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

class JusoAddressFinder:
    driver: Optional[WebDriver]
    url = 'https://www.juso.go.kr/openIndexPage.do'

    def __init__(self):
        self.driver = None

    def generate_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--window-size=1920,1080')
        options.add_experimental_option("detach", True)

        options.add_argument('--no-sandbox')
        options.add_argument('--headless')

        self.driver = webdriver.Chrome(
                executable_path=ChromeDriverManager().install(),
                options=options)

    def action_after_open_driver(self):
        try:
            # 광고창 닫기
            self.driver.find_element(By.CLASS_NAME, 'qustClose').click()
        except NoSuchElementException:
            # 광고창이 없을 수도 있음
            pass

    def open_driver(self):
        if not self.driver:
            self.generate_driver()
        
        self.driver.get(self.url)
        time.sleep(1)
        self.action_after_open_driver()

    def close_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def __del__(self):
        self.close_driver()

    def action_search_address(self, address: str, postal_code: str = ''):
        input_data = postal_code + ' ' + address
        try:
            input_form = self.driver.find_element(By.ID, 'inputSearchAddr')
        except NoSuchElementException:
            input_form = self.driver.find_element(By.ID, 'keyword')
        input_form.clear()
        input_form.send_keys(input_data)
        input_form.send_keys(Keys.ENTER)

    def get_searched_address(self) -> Tuple[str, str, str]:
        searched_address_forms = self.driver.find_elements(By.CLASS_NAME, 'addr_cont')

        if not searched_address_forms:
            return None, None, None

        searched_address_form = searched_address_forms[0]

        road_address_form = searched_address_form.find_element(By.ID, 'rnAddr1')
        local_address_form = searched_address_form.find_element(By.ID, 'lndnAddr1')
        postal_code_form = searched_address_form.find_element(By.ID, 'bsiZonNo1')

        road_address = road_address_form.get_attribute('value')
        local_address = local_address_form.get_attribute('value')
        postal_code = postal_code_form.get_attribute('value')

        if road_address:
            try:
                removed_idx = road_address.index('(')
                road_address = road_address[:removed_idx]
            except ValueError:
                pass

        return road_address, local_address, postal_code

    def search_address(
            self, address: str, postal_code: str = '') -> Tuple[str, str, str]:
        self.action_search_address(address, postal_code)
        return self.get_searched_address()
