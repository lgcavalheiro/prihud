from seleniumbase import Driver, page_actions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from database.scraping.interfaces import ScraperInterface


class ChromiumScraper(ScraperInterface):
    driver = None

    def __init__(self):
        super()
        self.driver = Driver(headless=True, headless2=True, uc=True)

    def __del__(self):
        if self.driver:
            self.driver.quit()

    def scrape(self, url):
        self.driver.get(url)
        return self.driver.page_source
