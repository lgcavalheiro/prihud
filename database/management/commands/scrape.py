import os
from django.core.management.base import BaseCommand
from database.models import Target, PriceHistory, Product
from selenium.common.exceptions import TimeoutException
from prihud.logger import AppriseLogger
from database.scrapping.command_wrapper import CommandWrapper
from datetime import datetime
from database.test_utils import TestLogger


class Command(BaseCommand):
    help = 'Run scraper for fetching price data'
    command_wrapper = None
    logger = None
    successes = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = TestLogger(
        ) if os.environ.get("TESTING") else AppriseLogger()
        self.command_wrapper = CommandWrapper(self.logger)

    def __del__(self):
        self.logger = None
        self.command_wrapper = None

    def handle(self, *args, **options):
        targets = Target.objects.all()
        start_msg = f'Starting scraping job with {len(targets)} targets'
        self.stdout.write(start_msg)
        self.logger.info(start_msg, f"Starting scrape job at {datetime.now()}")

        for target in targets:
            try:
                self.command_wrapper.scrape(target)
                self.successes += 1
            except TimeoutException as e:
                err_msg = f"Target timed out {target.alias or ''} {target.url}"
                self.stderr.write(err_msg)
                self.logger.fail(
                    err_msg, f"Target failed {target.alias or ''} {target.url}")
            except Exception as e:
                err_msg = f"Scraping target failed with {e}"
                self.stderr.write(err_msg)
                self.logger.fail(
                    err_msg, f"Target failed {target.alias or ''} {target.url}")

        end_msg = f'Scrape job finished with {self.successes} out of {len(targets)} successes'
        self.stdout.write(end_msg)
        self.logger.success(end_msg, f"Scrape job ended at {datetime.now()}")
