from distutils.spawn import find_executable
from selenium.webdriver import Firefox, FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
from database.scraping.impl.driver_scraper import DriverScraper
from database.scraping.impl.price_getter import PriceGetter
from database.scraping.impl.strategies import DefaultStrategy, CacheStrategy
from database.models import Statuses
from database.test_utils import TestLogger
from prihud.logger import AppriseLogger
from prihud.settings import DRIVER_PATH, TESTING


class BaseJob:
    price_getter, driver, scraper = None, None, None
    strategies = []

    error_handling_literals = {
        "PriceNotFoundException": ("Price not found: ", Statuses.PRICE_NOT_FOUND, False),
        "NoSelectorException": ("No selector set: ", Statuses.NO_SELECTOR, False)
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        options = FirefoxOptions()
        options.add_argument('--headless')
        options.set_preference("http.response.timeout", 30)
        options.set_preference("dom.max_script_run_time", 30)
        options.set_preference("dom.disable_beforeunload", True)
        options.set_preference("browser.tabs.warnOnClose", False)
        options.set_preference('permissions.default.image', 2)
        options.set_preference(
            'dom.ipc.plugins.enabled.libflashplayer.so', 'false')

        executable_path = DRIVER_PATH if (DRIVER_PATH and find_executable(
            DRIVER_PATH)) else GeckoDriverManager().install()
        service = Service(executable_path=executable_path)
        self.driver = Firefox(options=options, service=service)

        self.price_getter = PriceGetter(self.driver)
        self.scraper = DriverScraper(self.driver)
        self.strategies = [
            DefaultStrategy(self.scraper, self.price_getter),
            CacheStrategy(self.scraper, self.price_getter)
        ]

        self.load_cookies()

    def __del__(self):
        if self.driver:
            self.driver.quit()

    def load_cookies(self):
        raise NotImplementedError

    def __scrape_target(self, target):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError


class CanLog:
    logger = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = TestLogger() if TESTING else AppriseLogger()


class MultiTargetJob:
    targets = []

    def __init__(self, targets, **kwargs):
        super().__init__(**kwargs)
        self.targets = targets


class SingleTargetJob:
    target = None

    def __init__(self, target, **kwargs):
        super().__init__(**kwargs)
        self.target = target
