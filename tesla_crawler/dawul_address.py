import time
from typing import Dict, Tuple, Optional

from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class DawulAddressFinder:
    """
    다올주소검색사이트를 이용한
    주소 정제 및 위경도 추출
    """
    driver: Optional[WebDriver]
    url = 'https://address.dawul.co.kr'

    def __init__(self):
        self.driver = None

    def generate_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--window-size=1920,1080')
        options.add_experimental_option('detach', True)

        options.add_argument('--no-sandbox')
        options.add_argument('--headless')

        self.driver = webdriver.Chrome(
                executable_path=ChromeDriverManager().install(),
                options=options)

    def action_after_open_driver(self):
        # 팝업창 제거 
        for name in self.driver.window_handles[1:]:
            self.driver.switch_to.window(name)
            self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    def open_driver(self):
        if not self.driver:
            self.generate_driver()

        self.driver.get(self.url)
        self.driver.implicitly_wait(3)

        self.action_after_open_driver()

    def close_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def __del__(self):
        self.close_driver()

    def action_search_location(self, address: str):
        input_form = self.driver.find_element(By.ID, 'input_juso')
        input_form.clear()
        input_form.send_keys(address)
        input_form.send_keys(Keys.ENTER)
        time.sleep(1)
        
    def get_latitude_and_longitude(self, address: str) -> Dict[str, float]:
        self.action_search_location(address)
        raw_locations = self.driver.find_element(By.ID, 'insert_data_5').text
        raw_lng, raw_lat = raw_locations.split(', ')
        try:
            return {
                'latitude': float(raw_lat[3:]),
                'longitude': float(raw_lng[3:]),
            }
        except ValueError:
            return None

    def get_modified_address(self, address: str) -> Tuple[str, str]:
        """
        action_search_location을 먼저 호출해야 사용 가능

        도로명과 지역명이 나온다.
        그러나 둘 중 어느 것이 먼저 오는 지 알 수 없다. 
        """
        self.action_search_location(address)
        raw_address1 = self.driver.find_element(By.ID, 'insert_data_2').text
        raw_address2 = self.driver.find_element(By.ID, 'insert_data_3').text
        if raw_address1 == '정제결과없음':
            return None, None
        try:
            address1 = raw_address1[:raw_address1.index('(')-1]
        except ValueError:
            address1 = raw_address1
        
        address2 = ' '.join(raw_address2.split()[:-1])
        return address1, address2
