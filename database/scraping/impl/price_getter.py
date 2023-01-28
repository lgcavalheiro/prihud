import extruct
from database.scraping.interfaces import PriceGetterInterface


class PriceGetter(PriceGetterInterface):
    availabilities = ['InStock', 'PreOrder', 'PreSale',
                      'OnlineOnly', 'LimitedAvailability', 'InStoreOnly']

    def __init__(self):
        super()

    def get_price(self, page, url):
        metadata = extruct.extract(page,
                                   base_url=url,
                                   uniform=True,
                                   syntaxes=['json-ld',
                                             'microdata',
                                             'opengraph'])

        if not metadata:
            return None

        for data in metadata['json-ld']:
            if data['@type'] == 'Product':
                if data['offers']['availability'].split('/')[-1] not in self.availabilities:
                    print('Not in stock')
                price = data['offers']['price']
                return price
