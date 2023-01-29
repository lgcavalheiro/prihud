import requests
from database.scraping.interfaces import ScraperInterface


CACHE_URL = 'https://webcache.googleusercontent.com/search?q=cache:'


class CacheScraper(ScraperInterface):
    def __init__(self):
        super()

    def scrape(self, url):
        r = requests.get(f'{CACHE_URL}{url}')
        return r.text
