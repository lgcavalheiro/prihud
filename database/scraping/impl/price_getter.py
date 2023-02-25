"""
Module providing PriceGetter class.
Used for all price scraping tasks.
"""

import extruct
from database.scraping.exceptions import PriceNotFoundException, NoSelectorException
from database.scraping.interfaces import PriceGetterInterface

NOT_FOUND_CONST = -1


class PriceGetter(PriceGetterInterface):
    """ 
    PriceGetter class. 
    Gets prices from targets by means 
    of metadata scraping or page scraping. 
    """

    driver = None
    availabilities = ['InStock', 'PreOrder', 'PreSale',
                      'OnlineOnly', 'LimitedAvailability', 'InStoreOnly']

    def __init__(self, driver):
        super()
        self.driver = driver

    def __del__(self):
        if self.driver:
            self.driver.quit()

    def get_price_from_metadata(self, base_url):
        status = 'S'
        metadata = extruct.extract(self.driver.page_source,
                                   base_url=base_url,
                                   uniform=True,
                                   syntaxes=['json-ld',
                                             'microdata',
                                             'opengraph'])

        if not metadata:
            return (NOT_FOUND_CONST, NOT_FOUND_CONST)

        for data in metadata['json-ld']:
            if data['@type'] == 'Product':
                if data['offers']['availability'].split('/')[-1] not in self.availabilities:
                    status = 'O'
                price = data['offers']['price']
                return (price, status)

        return (NOT_FOUND_CONST, NOT_FOUND_CONST)

    def get_price_from_page(self, target):
        status = 'S'
        selector, selector_type = None, None

        if target.selector:
            selector, selector_type = target.selector.selector, target.selector.selector_type
        elif target.custom_selector and target.custom_selector_type:
            selector, selector_type = target.custom_selector, target.custom_selector_type
        else:
            raise NoSelectorException()

        price_tag = self.driver.find_element(by=selector_type, value=selector)
        price = price_tag.text.replace('R$', '').replace('\n', ',').replace(
            '.', '').replace(',', '.').strip()

        return (price, status)

    def get_price(self, target):
        (price, status) = self.get_price_from_metadata(target.url)
        if NOT_FOUND_CONST not in (price, status):
            return (price, status)

        (price, status) = self.get_price_from_page(target)
        if NOT_FOUND_CONST not in (price, status):
            return (price, status)

        raise PriceNotFoundException()
