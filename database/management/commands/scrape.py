from django.core.management.base import BaseCommand, CommandError
from database.models import Target, PriceHistory
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.firefox import GeckoDriverManager


class Command(BaseCommand):
    help = 'Run scraper for fetching price data'
    driver = None
    successes = 0
    selector_dict = {
        'css': By.CSS_SELECTOR,
        'xpath': By.XPATH,
        'tag': By.TAG_NAME,
        'class': By.CLASS_NAME,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

    def handle(self, *args, **options):
        targets = Target.objects.all()
        self.stdout.write(f'Starting scraping job with {len(targets)} targets')

        for target in targets:
            self.driver.get(target.url)
            element = WebDriverWait(driver=self.driver, timeout=5).until(
                EC.presence_of_element_located((self.selector_dict[target.selector_type], target.selector)))

            price_tag = self.driver.find_element(
                by=self.selector_dict[target.selector_type], value=target.selector)
            if not price_tag:
                self.stderr.write(
                    f'Price not found! Skipping {target.url} @ {target.product.name}')
                continue

            price = price_tag.text.replace('R$', '').replace(
                '.', '').replace(',', '.').strip()

            self.stdout.write(f"{target.url} --- {price}")
            price_history = PriceHistory(target=target, price=price)

            price_history.save(self)
            self.successes += 1

        self.stdout.write(
            f'Scraping job finished with {self.successes} successes')
