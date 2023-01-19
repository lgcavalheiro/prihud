from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class Scrapper():
    driver = None
    logger = None
    selector_dict = {
        'css': By.CSS_SELECTOR,
        'xpath': By.XPATH,
        'tag': By.TAG_NAME,
        'class': By.CLASS_NAME,
    }

    def __init__(self, logger, driver):
        self.driver = driver
        self.logger = logger

    def __del__(self):
        if self.driver:
            self.driver.quit()
        self.logger = None

    def find_element_or_fail(self, target):
        WebDriverWait(driver=self.driver, timeout=5).until(
            EC.presence_of_element_located((self.selector_dict[target.selector_type], target.selector)))

    def get_price_from_page(self, target):
        try:
            price_tag = self.driver.find_element(
                by=self.selector_dict[target.selector_type], value=target.selector)
            return price_tag.text.replace('R$', '').replace('.', '').replace(',', '.').strip()
        except:
            return None

    def go_to_page(self, url):
        self.driver.get(url)

    def get_page_info(self):
        page_source = self.driver.page_source
        current_url = self.driver.current_url
        return (page_source, current_url)

    def scrape_target(self, target):
        price = None
        status = 'S'

        if (self.driver.current_url != target.url):
            self.go_to_page(target.url)

        self.find_element_or_fail(target)
        price = self.get_price_from_page(target)

        if not price:
            err_msg = f'Price not found! Skipping {target.url} @ {target.product.name}'
            self.stderr.write(err_msg)
            self.logger.fail(
                err_msg, f'Price not found {target.alias or ""} {target.url}')
            raise Exception("Price not found")

        return (price, status)
