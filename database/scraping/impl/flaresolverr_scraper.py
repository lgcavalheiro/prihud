import requests
import json
from database.scraping.interfaces import ScraperInterface

ENDPOINT = "http://flaresolverr:8191"


class FlaresolverrScraper(ScraperInterface):
    def __init__(self):
        super()
        requests.post(ENDPOINT, {"cmd": "sessions.create"})

    def __del__(self):
        requests.post(ENDPOINT, {"cmd": "sessions.destroy"})

    def scrape(self, url):
        data = json.dumps(
            {"cmd": "request.get", "url": url, "maxTimeout": 60000})
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(f'{ENDPOINT}/v1', data=data, headers=headers)
        response = response.json()
        return response["solution"]["response"]
