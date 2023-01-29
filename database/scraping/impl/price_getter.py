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
        metadata = extruct.extract(page,
                                   base_url=base_url,
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

    def get_price_from_page(self, target):
        try:
            price_tag = self.driver.find_element(
                by=self.selector_dict[target.selector_type], value=target.selector)
            return price_tag.text.replace('R$', '').replace('.', '').replace(',', '.').strip()
        except:
            return None

    def get_price(self, page, target):
        price = self.get_price_from_metadata(page, target.url)
        if price:
            return price
        return self.get_price_from_page(target)
