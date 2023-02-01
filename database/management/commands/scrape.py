import os
from django.core.management.base import BaseCommand
from distutils.spawn import find_executable
from selenium.webdriver import Firefox, FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager
from datetime import datetime
from database.scraping.impl.driver_scraper import DriverScraper
from database.scraping.impl.price_getter import PriceGetter
from database.scraping.exceptions import PriceNotFoundException
from database.models import Target, PriceHistory
from prihud.logger import AppriseLogger
from database.test_utils import TestLogger
from prihud.settings import DRIVER_PATH


class Command(BaseCommand):
    help = 'Run scraper for fetching price data'
    price_getter = None
    scraper = None
    logger = None
    successes = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        options = FirefoxOptions()
        options.add_argument('--headless')
        options.set_preference('permissions.default.image', 2)
        options.set_preference(
            'dom.ipc.plugins.enabled.libflashplayer.so', 'false')

        if (DRIVER_PATH and find_executable(DRIVER_PATH)):
            executable_path = DRIVER_PATH
        else:
            executable_path = GeckoDriverManager().install()
        driver = Firefox(options=options, executable_path=executable_path)

        self.logger = TestLogger() if os.environ.get("TESTING") else AppriseLogger()
        self.price_getter = PriceGetter(driver)
        self.scraper = DriverScraper(driver)

    def __del__(self):
        self.price_getter = None
        self.driver = None

    def log_message(self, msg, is_error=False):
        if is_error:
            self.logger.fail(msg)
            self.stderr.write(msg)
        else:
            self.logger.info(msg)
            self.stdout.write(msg)

    def save_target_status(self, target, status):
        target.status = status
        target.save()

    def save_price_history(self, target, price, status):
        if (os.environ.get("TESTING")):
            self.log_message("Not saving due to testing environment")
            return

        if target.status != status:
            self.save_target_status(target, status)

        if status == target.Statuses.SUCCESS:
            price_history = PriceHistory(target=target, price=price)
            price_history.save()

    def scrape_target(self, target):
        def execute_strategy(self, target, use_cache=False):
            try:
                page = self.scraper.scrape(target.url, use_cache=use_cache)
                (price, status) = self.price_getter.get_price(page, target)
                return (price, status)
            except Exception as e:
                self.log_message(
                    f'Target failed, trying next strategy {target.alias if target.alias else target.url}: {e}')
                return ("ERROR", target.Statuses.UNDEFINED)

        strategies = {
            'standard': {'use_cache': False},
            'cache_approach': {'use_cache': True},
        }

        for (key, value) in strategies.items():
            (price, status) = execute_strategy(
                self, target, use_cache=value['use_cache'])
            if price != "ERROR":
                self.log_message(
                    f"Strategy [{key}] found price: {price} - {status} - {target.url}")
                return (price, status)

        raise PriceNotFoundException

    def handle(self, *args, **options):
        targets = Target.objects.all()
        self.log_message(
            f'Starting scraping job with {len(targets)} targets at {datetime.now()}')

        for target in targets:
            try:
                (price, status) = self.scrape_target(target)
                self.save_price_history(target, price, status)
                self.successes += 1
            except PriceNotFoundException:
                self.log_message(
                    f'Price not found: {target.url}', is_error=True)
                self.save_target_status(target, target.Statuses.UNDEFINED)
            except Exception as e:
                self.log_message(f'Target failed: {e}', is_error=True)
                self.save_target_status(target, target.Statuses.UNDEFINED)

        self.log_message(
            f'Finished scraping job with {self.successes}/{len(targets)} successes at {datetime.now()}')
