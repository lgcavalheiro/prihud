import extruct
from django.core.management.base import BaseCommand
from database.models import Target, PriceHistory, Product
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.firefox import GeckoDriverManager
from prihud.logger import AppriseLogger
from datetime import datetime


class Command(BaseCommand):
    help = 'Run scraper for fetching price data'
    driver = None
    logger = None
    successes = 0
    selector_dict = {
        'css': By.CSS_SELECTOR,
        'xpath': By.XPATH,
        'tag': By.TAG_NAME,
        'class': By.CLASS_NAME,
    }
    availabilities = ['InStock', 'PreOrder', 'PreSale',
                      'OnlineOnly', 'LimitedAvailability', 'InStoreOnly']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = AppriseLogger()
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        options.set_preference('permissions.default.image', 2)
        options.set_preference(
            'dom.ipc.plugins.enabled.libflashplayer.so', 'false')
        self.driver = webdriver.Firefox(
            options=options, executable_path=GeckoDriverManager().install())

    def __del__(self):
        if self.driver:
            self.driver.quit()
        self.logger = None

    def add_arguments(self, parser):
        parser.add_argument(
            '--target',
            type=str,
            help='Custom target url to scrape',
        )

    def find_metadata(self):
        return extruct.extract(self.driver.page_source,
                               base_url=self.driver.current_url,
                               uniform=True,
                               syntaxes=['json-ld',
                                         'microdata',
                                         'opengraph'])

    def find_element_or_fail(self, target):
        WebDriverWait(driver=self.driver, timeout=5).until(
            EC.presence_of_element_located((self.selector_dict[target.selector_type], target.selector)))

    def get_price_from_page(self, target):
        try:
            price_tag = self.driver.find_element(
                by=self.selector_dict[target.selector_type], value=target.selector)
            return price_tag.text.replace('R$', '').replace('.', '').replace(',', '.').strip()
        except:
            return None

    def get_price_from_metadata(self, metadata, url):
        status = 'S'
        try:
            for data in metadata['json-ld']:
                if data['@type'] == 'Product':
                    if data['offers']['availability'].split('/')[-1] not in self.availabilities:
                        status = 'O'
                        self.logger.warn(
                            f"Target is not in stock: {url} {data['offers']['availability']}")
                    return {'price': data['offers']['price'], 'status': status}
        except:
            return {'price': None, 'status': 'U'}
        finally:
            return {'price': None, 'status': 'U'}

    def save_price_history(self, target, price, status):
        self.stdout.write(
            f"{target.url} --- {price} --- {status}")
        price_history = PriceHistory(target=target, price=price, status=status)
        price_history.save(self)

    def scrape_target(self, target):
        self.driver.get(target.url)
        metadata = self.find_metadata()
        price = None
        status = 'S'

        if metadata:
            metadata_res = self.get_price_from_metadata(metadata, target.url)
            price = metadata_res['price']
            status = metadata_res['status']

        if metadata and not price:
            self.find_element_or_fail(target)
            price = self.get_price_from_page(target)

        if not price:
            err_msg = f'Price not found! Skipping {target.url} @ {target.product.name}'
            self.stderr.write(err_msg)
            self.logger.fail(
                err_msg, f'Price not found {target.alias or ""} {target.url}')
            raise Exception("Price not found")

        self.save_price_history(target, price, status)

    def handle(self, *args, **options):
        if options['target']:
            target = Target(url=options['target'],
                            selector_type='xpath',
                            selector="/html/body/div[7]/div/div[2]/div/div[2]/div[4]/div[2]/div[1]/span[1]",
                            product=Product(name="custom"))
            self.scrape_target(target)
            return

        targets = Target.objects.all()
        start_msg = f'Starting scraping job with {len(targets)} targets'
        self.stdout.write(start_msg)
        self.logger.info(
            start_msg, f"Starting scrape job at {datetime.now()}")

        for target in targets:
            try:
                self.scrape_target(target)
                self.successes += 1
            except TimeoutException as e:
                err_msg = f"Target timed out {target.alias or ''} {target.url}"
                self.stderr.write(err_msg)
                self.logger.fail(
                    err_msg, f"Target failed {target.alias or ''} {target.url}")
            except Exception as e:
                err_msg = f"Scraping target failed with {e}"
                self.stderr.write(err_msg)
                self.logger.fail(
                    err_msg, f"Target failed {target.alias or ''} {target.url}")

        end_msg = f'Scrape job finished with {self.successes} out of {len(targets)} successes'
        self.stdout.write(end_msg)
        self.logger.success(end_msg, f"Scrape job ended at {datetime.now()}")
