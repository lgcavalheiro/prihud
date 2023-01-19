import os
from distutils.spawn import find_executable
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from .metadata_scrapper import MetadataScrapper
from .scrapper import Scrapper
from database.models import PriceHistory
from prihud.settings import DRIVER_PATH


class CommandWrapper():
    metadata_scrapper = None
    scrapper = None
    logger = None

    def __init__(self, logger):
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        options.set_preference('permissions.default.image', 2)
        options.set_preference(
            'dom.ipc.plugins.enabled.libflashplayer.so', 'false')

        if (DRIVER_PATH and find_executable(DRIVER_PATH)):
            executable_path = DRIVER_PATH
        else:
            executable_path = GeckoDriverManager().install()
        driver = webdriver.Firefox(
            options=options, executable_path=executable_path)

        self.logger = logger
        self.metadata_scrapper = MetadataScrapper(logger)
        self.scrapper = Scrapper(logger, driver)

    def __del__(self):
        self.metadata_scrapper = None
        self.scrapper = None

    def scrape(self, target):
        self.scrapper.go_to_page(target.url)
        (page_source, current_url) = self.scrapper.get_page_info()

        (price, status) = self.metadata_scrapper.get_price_from_metadata(
            page_source, current_url)
        if (price):
            print("Using metadata price")
            self.save_price_history(target, price, status)
            return

        (price, status) = self.scrapper.scrape_target(target)
        if (price):
            print("Using page price")
            self.save_price_history(target, price, status)
            return

        raise Exception("Price not found!")

    def save_price_history(self, target, price, status):
        print(f"{target.url} --- {price} --- {status}")
        price_history = PriceHistory(target=target, price=price, status=status)
        if (os.environ.get("TESTING")):
            print("Not saving due to testing environment")
        else:
            price_history.save()
