class PriceNotFoundException(Exception):
    def __str__(self):
        return self.__class__.__name__


class NoSelectorException(Exception):
    def __str__(self):
        return self.__class__.__name__
