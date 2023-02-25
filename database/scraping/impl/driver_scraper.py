"""
Module providing DriverScraper class.
Used for navigating targets using the provided webdriver.
"""

from database.scraping.interfaces import ScraperInterface


CACHE_URL = 'https://webcache.googleusercontent.com/search?q=cache:'


class DriverScraper(ScraperInterface):
    """ DriverScraper class. Used for all target navigation. """

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
