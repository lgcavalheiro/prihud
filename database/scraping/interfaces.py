import abc


class ScraperInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'scrape') and callable(subclass.scrape) or NotImplemented)

    @abc.abstractmethod
    def scrape(self, url):
        raise NotImplementedError


class PriceGetterInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'get_price') and callable(subclass.get_price) or NotImplemented)

    @abc.abstractmethod
    def get_price(self, page):
        return NotImplementedError

    @abc.abstractmethod
    def get_price_from_metadata(self, page, base_url):
        return NotImplementedError

    @abc.abstractmethod
    def get_price_from_page(self, target):
        return NotImplementedError


class StrategyInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'execute') and callable(subclass.execute) or NotImplemented)

    @abc.abstractmethod
    def execute(self, target) -> (str, str):
        return NotImplementedError
