from django.core.management.base import BaseCommand
from database.scraping.impl.chromium_scraper import ChromiumScraper
from database.scraping.impl.price_getter import PriceGetter
from database.models import Target


class Command(BaseCommand):
    help = 'Run scraper for fetching price data'
    scraper = None
    price_getter = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scraper = ChromiumScraper()
        self.price_getter = PriceGetter()

    def __del__(self):
        self.scraper = None

    def scrape_target(self, target):
        page = self.scraper.scrape(target.url)
        price = self.price_getter.get_price(page, target.url)
        print(f'Found price: {price} - {target.url}')

    def handle(self, *args, **options):
        targets = Target.objects.all()

        for target in targets:
            self.scrape_target(target)
