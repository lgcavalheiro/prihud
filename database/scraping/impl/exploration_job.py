""" 
Module providing ExplorationJob class. 
Used for performing exploratory scraping from the frontend.
"""

from datetime import datetime
from database.scraping.exceptions import PriceNotFoundException
from database.scraping.base import BaseJob, CanLog, SingleTargetJob
from database.models import Statuses, Cookie


class ExplorationJob(BaseJob, SingleTargetJob, CanLog):
    """ ExplorationJob class, used for exploratory scraping of a single target """

    report, start_time, end_time = None, None, None

    def __init__(self, target, **kwargs):
        super().__init__(target=target, **kwargs)

    def load_cookies(self):
        cookies = Cookie.get_all_grouped()
        if cookies:
            for [key, value] in cookies.items():
                self.driver.get(key)
                for cookie in value:
                    self.driver.add_cookie(cookie.get_parsed())

    def __scrape_target(self, target):
        for strategy in self.strategies:
            (price, status) = strategy.execute(target)
            return (price, status)

        raise PriceNotFoundException

    def start(self):
        self.start_time = datetime.now()

        try:
            (price, status) = self.__scrape_target(self.target)
        except Exception as error:
            (msg, status) = self.error_handling_literals.get(
                error.__class__.__name__, ("Target failed: ", Statuses.UNDEFINED))
            return {
                "success": False,
                "message": f'{msg}{self.target.url}',
                "status": status,
                "error": str(error),
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
