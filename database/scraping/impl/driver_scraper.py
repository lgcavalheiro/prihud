import requests
from database.scraping.interfaces import ScraperInterface


CACHE_URL = 'https://webcache.googleusercontent.com/search?q=cache:'


class DriverScraper(ScraperInterface):
    driver = None

    def __init__(self, driver):
        super()
        self.driver = driver

    def __del__(self):
        if self.driver:
            self.driver.quit()

    def scrape(self, url, use_cache=False):
        if use_cache:
            url = f'{CACHE_URL}{url}'
        self.driver.get(url)
        return self.driver.page_source
