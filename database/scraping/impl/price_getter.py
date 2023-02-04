import extruct
from database.scraping.exceptions import PriceNotFoundException
from database.scraping.interfaces import PriceGetterInterface

NOT_FOUND_CONST = -1


class PriceGetter(PriceGetterInterface):
    driver = None
    availabilities = ['InStock', 'PreOrder', 'PreSale',
                      'OnlineOnly', 'LimitedAvailability', 'InStoreOnly']

    def __init__(self, driver):
        super()
        self.driver = driver

    def __del__(self):
        if self.driver:
            self.driver.quit()

    def get_price_from_metadata(self, page, base_url):
        status = 'S'
        metadata = extruct.extract(page,
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
        else:
            return (NOT_FOUND_CONST, NOT_FOUND_CONST)

    def get_price_from_page(self, target):
        status = 'S'
        price_tag = self.driver.find_element(
            by=target.selector_type, value=target.selector)
        price = price_tag.text.replace('R$', '').replace(
            '.', '').replace(',', '.').strip()
        return (price, status)

    def get_price(self, page, target):
        (price, status) = self.get_price_from_metadata(page, target.url)
        if price != NOT_FOUND_CONST and status != NOT_FOUND_CONST:
            return (price, status)

        (price, status) = self.get_price_from_page(target)
        if price != NOT_FOUND_CONST and status != NOT_FOUND_CONST:
            return (price, status)

        raise PriceNotFoundException()
