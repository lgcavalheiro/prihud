import requests
from database.scraping.interfaces import ScraperInterface


class RequestsScraper(ScraperInterface):
    def __init__(self):
        super()

    def scrape(self, url):
        r = requests.get(url)
        return r.text
