import os
from distutils.spawn import find_executable
from selenium.webdriver import Firefox, FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager
from datetime import datetime
from database.scraping.impl.driver_scraper import DriverScraper
from database.scraping.impl.price_getter import PriceGetter
from database.scraping.impl.strategies import DefaultStrategy, CacheStrategy
from database.scraping.exceptions import PriceNotFoundException, NoSelectorException
from database.models import PriceHistory, Statuses, Cookie
from prihud.settings import DRIVER_PATH, TESTING


class ExplorationJob:
    price_getter, scraper, report, target = None, None, None, None
    strategies = []

    def __init__(self, target):
        self.target = target
        options = FirefoxOptions()
        options.add_argument('--headless')
        options.set_preference('permissions.default.image', 2)
        options.set_preference(
            'dom.ipc.plugins.enabled.libflashplayer.so', 'false')

        executable_path = DRIVER_PATH if (DRIVER_PATH and find_executable(
            DRIVER_PATH)) else GeckoDriverManager().install()
        driver = Firefox(options=options, executable_path=executable_path)

        self.price_getter = PriceGetter(driver)
        self.scraper = DriverScraper(driver)
        self.strategies = [
            DefaultStrategy(self.scraper, self.price_getter),
            CacheStrategy(self.scraper, self.price_getter)
        ]

        cookies = Cookie.get_all_grouped()
        if cookies:
            for key in cookies.keys():
                driver.get(key)
                for cookie in cookies[key]:
                    driver.add_cookie(cookie.get_parsed())

    def __del__(self):
        self.price_getter = None
        self.scraper = None

    def scrape_target(self, target):
        for strategy in self.strategies:
            (price, status) = strategy.execute(target)
            return (price, status)

        raise PriceNotFoundException

    def start(self):
        self.start_time = datetime.now()

        error_handling_literals = {
            "PriceNotFoundException": ("Price not found: ", Statuses.PRICE_NOT_FOUND),
            "NoSelectorException": ("No selector set: ", Statuses.NO_SELECTOR)
        }

        try:
            (price, status) = self.scrape_target(self.target)
        except Exception as e:
            (msg, status) = error_handling_literals.get(
                e.__class__.__name__, ("Target failed: ", Statuses.UNDEFINED))
            return {
                "success": False,
                "message": f'{msg}{self.target.url}',
                "status": status,
                "error": e,
                "page_source": self.scraper.driver.page_source
            }

        self.end_time = datetime.now()

        return {
            "success": True,
            "status": status,
            "price": price,
            "page_source": self.scraper.driver.page_source,
            'start_time': self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            'end_time': self.end_time.strftime("%Y-%m-%d %H:%M:%S"),
            'duration': (self.end_time - self.start_time).total_seconds()
        }
