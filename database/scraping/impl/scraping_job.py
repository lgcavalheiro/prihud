"""
Module providing ScrapingJob class.
Used for general scraping tasks.
"""

from datetime import datetime
from database.scraping.exceptions import PriceNotFoundException, CacheNotChangedException
from database.scraping.base import BaseJob, CanLog, MultiTargetJob
from database.models import PriceHistory, Statuses, Cookie
from prihud.settings import TESTING


class ScrapingJob(BaseJob, MultiTargetJob, CanLog):
    """
    ScrapingJob class.
    Used for all recurrent scraping tasks 
    that feed the application's database.
    """

    start_time, end_time = None, None
    failures = []
    successes = 0

    def __init__(self, targets, **kwargs):
        super().__init__(targets=targets, **kwargs)

    def load_cookies(self):
        cookies = Cookie.get_all_grouped()
        if cookies:
            self.logger.info(
                f'Adding cookies from: {",".join(cookies.keys())}')
            for [key, value] in cookies.items():
                self.driver.get(key)
                for cookie in value:
                    self.driver.add_cookie(cookie.get_parsed())

    def save_target_status(self, target, status):
        """ Saves target status if said status has changed compared to database """

        if target.status != status:
            target.status = status
            target.save()

    def __save_price_history(self, target, price, status):
        if TESTING:
            self.logger.info("Not saving due to testing environment")
            return

        self.save_target_status(target, status)

        if status == Statuses.SUCCESS:
            price_history = PriceHistory(target=target, price=price)
            price_history.save()

    def __scrape_target(self, target):
        for strategy in self.strategies:
            try:
                (price, status) = strategy.execute(target)
                self.logger.info(' '.join([
                    f'Strategy [{strategy.__class__.__name__}] found price:',
                    f"{price} - {dict(Statuses.choices).get(status, 'UNMAPPED STATUS')} -",
                    target.url]))
                return (price, status)
            except CacheNotChangedException as error:
                self.logger.info(
                    f'Target already has cached price: {target.alias or target.url}')
                raise error
            except Exception as error:
                self.logger.warn(
                    f'Target failed, trying next strategy {target.alias or target.url}: {error}')

        raise PriceNotFoundException

    def start(self):
        self.start_time = datetime.now()
        self.logger.info(
            f'Starting scraping job with {len(self.targets)} targets at {self.start_time}')

        for target in self.targets:
            try:
                self.logger.info(f'==== {target.alias or target.url} ====')
                (price, status) = self.__scrape_target(target)
                self.__save_price_history(target, price, status)
                self.successes += 1
            except CacheNotChangedException:
                self.save_target_status(target, Statuses.CACHED)
                self.successes += 1
            except Exception as error:
                (msg, status, log_error) = self.error_handling_literals.get(
                    error.__class__.__name__, ("Target failed: ", Statuses.UNDEFINED, True))
                self.failures.append((target, error))
                self.save_target_status(target, status)
                self.logger.fail(
                    f"{msg}{target.url} {error if log_error else ''}")

        self.end_time = datetime.now()
        self.logger.success(' '.join([
            'Finished scraping job with',
            f'{self.successes}/{len(self.targets)}',
            f'successes at {self.end_time}']))
        self.logger.success(
            f'Total duration: {self.end_time - self.start_time}')

        if len(self.failures) > 0:
            self.logger.fail(
                f"=== Had {len(self.failures)} failures ===")
            for failure in self.failures:
                self.logger.fail(
                    f'{failure[0].alias or failure[0].url}: {failure[1]}')

        return {
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': self.end_time - self.start_time,
            'result': f'{self.successes}/{len(self.targets)}',
            'failures': self.failures
        }
