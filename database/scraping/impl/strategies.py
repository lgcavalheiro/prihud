""" Module providing all strategy implementations. """

from ..interfaces import StrategyInterface
from ..exceptions import CacheNotChangedException


class DefaultStrategy(StrategyInterface):
    # pylint: disable=too-few-public-methods

    """ Default strategy for scraping prices from targets. """

    price_getter, scraper = None, None

    def __init__(self, scraper, price_getter):
        self.scraper = scraper
        self.price_getter = price_getter

    def execute(self, target):
        self.scraper.scrape(target.url)
        (price, status) = self.price_getter.get_price(target)
        return (price, status)


class CacheStrategy(StrategyInterface):
    # pylint: disable=too-few-public-methods

    """ Strategy for scraping prices from targets by using their
    google cached page, if one existis """

    price_getter, scraper = None, None

    def __init__(self, scraper, price_getter):
        self.scraper = scraper
        self.price_getter = price_getter

    def execute(self, target):
        self.scraper.scrape(target.url, use_cache=True)
        (price, status) = self.price_getter.get_price(target)
        recent_price = target.get_recent_price_history().price
        if recent_price == float(price):
            raise CacheNotChangedException()
        return (price, status)
