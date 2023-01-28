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
