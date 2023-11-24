import time

from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class TranslatorCrawler:
    url = "https://www.google.com/search?q=%EA%B5%AC%EA%B8%80+%EB%B2%88%EC%97%AD%EA%B8%B0&oq=%EA%B5%AC%EA%B8%80+%EB%B2%88%EC%97%AD%EA%B8%B0&aqs=chrome.0.69i59j0i131i433i512j0i512l8.1344j0j7&sourceid=chrome&ie=UTF-8"
    driver = None

    def generate_driver(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")

        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        self.driver = driver

    def open_driver(self):
        self.generate_driver()
        self.driver.get(self.url)
        self.driver.implicitly_wait(10)

    def translate(self, english_text: str) -> str:
        input_text_form = self.driver.find_element(By.ID, "tw-source-text-ta")
        output_text_form = self.driver.find_element(
            By.ID, "tw-target-text"
        ).find_element(By.TAG_NAME, "span")
        input_text_form.clear()
        input_text_form.send_keys(english_text)
        input_text_form.send_keys(Keys.ENTER)
        time.sleep(2)
        return output_text_form.text

    def close_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def __del__(self):
        self.close_driver()
