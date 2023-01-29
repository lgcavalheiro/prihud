from django.core.management.base import BaseCommand
from distutils.spawn import find_executable
from selenium.webdriver import Firefox, FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager
from database.scraping.impl.driver_scraper import DriverScraper
from database.scraping.impl.price_getter import PriceGetter
from database.models import Target
from prihud.settings import DRIVER_PATH


class Command(BaseCommand):
    help = 'Run scraper for fetching price data'
    price_getter = None
    scraper = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        options = FirefoxOptions()
        options.add_argument('--headless')
        options.set_preference('permissions.default.image', 2)
        options.set_preference(
            'dom.ipc.plugins.enabled.libflashplayer.so', 'false')

        if (DRIVER_PATH and find_executable(DRIVER_PATH)):
            executable_path = DRIVER_PATH
        else:
            executable_path = GeckoDriverManager().install()
        driver = Firefox(options=options, executable_path=executable_path)

        self.price_getter = PriceGetter(driver)
        self.scraper = DriverScraper(driver)

    def __del__(self):
        self.price_getter = None
        self.driver = None

    def scrape_target(self, target):
        page = self.scraper.scrape(target.url)
        price = self.price_getter.get_price(page, target)
        if price:
            print(f'Found price: {price} - {target.url}')
            return

        page = self.scraper.scrape(target.url, use_cache=True)
        price = self.price_getter.get_price(page, target)

        print(f'Found cached price: {price} - {target.url}')

    def handle(self, *args, **options):
        targets = Target.objects.all()

        for target in targets:
            self.scrape_target(target)
