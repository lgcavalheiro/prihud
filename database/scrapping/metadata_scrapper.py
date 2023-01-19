import extruct


class MetadataScrapper():
    logger = None
    availabilities = ['InStock', 'PreOrder', 'PreSale',
                      'OnlineOnly', 'LimitedAvailability', 'InStoreOnly']

    def __init__(self, logger):
        self.logger = logger

    def __del__(self):
        self.logger = None

    def find_metadata(self, page_source, base_url):
        return extruct.extract(page_source,
                               base_url=base_url,
                               uniform=True,
                               syntaxes=['json-ld',
                                         'microdata',
                                         'opengraph'])

    def get_price_from_metadata(self, page_source, url):
        status = 'S'
        price = None
        try:
            metadata = self.find_metadata(page_source, url)
            for data in metadata['json-ld']:
                if data['@type'] == 'Product':
                    if data['offers']['availability'].split('/')[-1] not in self.availabilities:
                        status = 'O'
                        self.logger.warn(
                            f"Target is not in stock: {url} {data['offers']['availability']}")
                    price = data['offers']['price']
                    return (price, status)
        except:
            status = 'U'
            return (price, status)
        finally:
            return (price, status)
