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
from prihud.settings import DRIVER_PATH, TESTING


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

        executable_path = DRIVER_PATH if (DRIVER_PATH and find_executable(
            DRIVER_PATH)) else GeckoDriverManager().install()
        driver = Firefox(options=options, executable_path=executable_path)

        self.logger = TestLogger() if TESTING else AppriseLogger()
        self.price_getter = PriceGetter(driver)
        self.scraper = DriverScraper(driver)

    def __del__(self):
        self.price_getter = None
        self.driver = None

    def log_message(self, msg, is_error=False):
        # should use logger or terminal
        log_key = 'F' if TESTING else 'T'
        # is it an error message or not
        log_key += 'F' if not is_error else 'T'

        log_literals = {
            "TT": lambda msg: self.logger.fail(msg),
            "TF": lambda msg: self.logger.info(msg),
            "FT": lambda msg: self.stderr.write(msg),
            "FF": lambda msg: self.stdout.write(msg)
        }

        log_literals.get(log_key)(msg)

    def save_target_status(self, target, status):
        target.status = status
        target.save()

    def save_price_history(self, target, price, status):
        if TESTING:
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

        # lambda self, target: self.strategy(target)
        strategies = {
            'standard': {'use_cache': False},
            'cache_approach': {'use_cache': True},
        }

        for (key, value) in strategies.items():
            (price, status) = execute_strategy(
                self, target, use_cache=value['use_cache'])
            if price != "ERROR":
                self.log_message(
                    f"Strategy [{key}] found price: {price} - {dict(target.Statuses.choices).get(status, 'UNMAPPED STATUS')} - {target.url}")
                return (price, status)

        raise PriceNotFoundException

    def add_arguments(self, parser):
        parser.add_argument('-f', type=str, dest='frequency',
                            help='Defines the target frequency to scrape')

        parser.add_argument('-i', type=int, dest='ids', action="append",
                            help="Defines only some targets to be scraped by their id")

    def handle(self, *args, **options):
        if (options['ids']):
            targets = Target.objects.filter(pk__in=options['ids']).all()
        else:
            targets = Target.objects.filter(
                frequency=options["frequency"]).all()

        if len(targets) == 0:
            self.log_message(
                f"Found no targets for this scraping job: [{dict(Target.Frequencies.choices).get(options['frequency'], 'UNMAPPED FREQUENCY')}]")
            return

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
                self.log_message(
                    f'Target failed {target.url}: {e}', is_error=True)
                self.save_target_status(target, target.Statuses.UNDEFINED)

        self.log_message(
            f'Finished scraping job with {self.successes}/{len(targets)} successes at {datetime.now()}')
