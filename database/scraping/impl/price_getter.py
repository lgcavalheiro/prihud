import extruct
from selenium.webdriver.common.by import By
from database.scraping.interfaces import PriceGetterInterface


class PriceGetter(PriceGetterInterface):
    driver = None
    availabilities = ['InStock', 'PreOrder', 'PreSale',
                      'OnlineOnly', 'LimitedAvailability', 'InStoreOnly']
    selector_dict = {
        'css': By.CSS_SELECTOR,
        'xpath': By.XPATH,
        'tag': By.TAG_NAME,
        'class': By.CLASS_NAME,
    }

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
            return (None, None)

        for data in metadata['json-ld']:
            if data['@type'] == 'Product':
                if data['offers']['availability'].split('/')[-1] not in self.availabilities:
                    status = 'O'
                price = data['offers']['price']
                return (price, status)

    def get_price_from_page(self, target):
        status = 'S'
        price_tag = self.driver.find_element(
            by=self.selector_dict[target.selector_type], value=target.selector)
        price = price_tag.text.replace('R$', '').replace(
            '.', '').replace(',', '.').strip()
        return (price, status)
        

    def get_price(self, page, target):
        (price, status) = self.get_price_from_metadata(page, target.url)
        if price and status:
            return (price, status)
        return self.get_price_from_page(target)
