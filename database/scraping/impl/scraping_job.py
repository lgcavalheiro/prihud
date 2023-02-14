import os
from distutils.spawn import find_executable
from selenium.webdriver import Firefox, FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager
from datetime import datetime
from database.scraping.impl.driver_scraper import DriverScraper
from database.scraping.impl.price_getter import PriceGetter
from database.scraping.exceptions import PriceNotFoundException, NoSelectorException
from database.models import PriceHistory, Statuses, Cookie
from prihud.logger import AppriseLogger
from database.test_utils import TestLogger
from prihud.settings import DRIVER_PATH, TESTING


class ScrapingJob():
    price_getter, scraper, logger, start_time, end_time = None, None, None, None, None
    targets, failures = [], []
    successes = 0

    def __init__(self, targets):
        self.targets = targets

        options = FirefoxOptions()
        options.add_argument('--headless')
        options.set_preference('permissions.default.image', 2)
        options.set_preference(
            'dom.ipc.plugins.enabled.libflashplayer.so', 'false')

        executable_path = DRIVER_PATH if (DRIVER_PATH and find_executable(
            DRIVER_PATH)) else GeckoDriverManager().install()
        driver = Firefox(options=options, executable_path=executable_path)

        self.logger = TestLogger() if TESTING else AppriseLogger()
        self.price_getter = PriceGetter(driver)
        self.scraper = DriverScraper(driver)

        cookies = Cookie.get_all_grouped()
        if cookies:
            self.logger.info(
                f'Adding cookies from: {",".join(cookies.keys())}')
            for key in cookies.keys():
                driver.get(key)
                for cookie in cookies[key]:
                    driver.add_cookie(cookie.get_parsed())

    def __del__(self):
        self.price_getter = None
        self.driver = None
        self.logger = None

    def save_target_status(self, target, status):
        if target.status != status:
            target.status = status
            target.save()

    def save_price_history(self, target, price, status):
        if TESTING:
            self.logger.info("Not saving due to testing environment")
            return

        self.save_target_status(target, status)

        if status == Statuses.SUCCESS:
            price_history = PriceHistory(target=target, price=price)
            price_history.save()

    def scrape_target(self, target):
        def execute_strategy(self, target, use_cache=False):
            try:
                page = self.scraper.scrape(target.url, use_cache=use_cache)
                (price, status) = self.price_getter.get_price(page, target)
                return (price, status)
            except Exception as e:
                self.logger.warn(
                    f'Target failed, trying next strategy {target.alias or target.url}: {e}')
                return ("ERROR", Statuses.UNDEFINED)

        # lambda self, target: self.strategy(target)
        strategies = {
            'standard': {'use_cache': False},
            'cache_approach': {'use_cache': True},
        }

        for (key, value) in strategies.items():
            (price, status) = execute_strategy(
                self, target, use_cache=value['use_cache'])
            if price != "ERROR":
                self.logger.info(
                    f"Strategy [{key}] found price: {price} - {dict(Statuses.choices).get(status, 'UNMAPPED STATUS')} - {target.url}")
                return (price, status)

        raise PriceNotFoundException

    def start(self):
        self.start_time = datetime.now()
        self.logger.info(
            f'Starting scraping job with {len(self.targets)} targets at {self.start_time}')

        for target in self.targets:
            try:
                self.logger.info(f'==== {target.alias or target.url} ====')
                (price, status) = self.scrape_target(target)
                self.save_price_history(target, price, status)
                self.successes += 1
            except PriceNotFoundException as e:
                self.logger.fail(f'Price not found: {target.url}')
                self.failures.append((target, e))
                self.save_target_status(target, Statuses.PRICE_NOT_FOUND)
            except NoSelectorException as e:
                self.logger.fail(f'No selector set: {target.url}')
                self.failures.append((target, e))
                self.save_target_status(target, Statuses.NO_SELECTOR)
            except Exception as e:
                self.logger.fail(f'Target failed {target.url}: {e}')
                self.failures.append((target, e))
                self.save_target_status(target, Statuses.UNDEFINED)

        self.end_time = datetime.now()
        self.logger.success(
            f'Finished scraping job with {self.successes}/{len(self.targets)} successes at {self.end_time}')
        self.logger.success(
            f'Total duration: {self.end_time - self.start_time}')

        if len(self.failures) > 0:
            self.logger.fail(
                f"=== Had {len(self.failures)} failures ===")
            for failure in self.failures:
                self.logger.fail(
                    f'{failure[0].alias or failure[0].url}: {failure[1]}')

    def get_report(self):
        return {
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': self.end_time - self.start_time,
            'result': f'{self.successes}/{len(self.targets)}',
            'failures': self.failures
        }
