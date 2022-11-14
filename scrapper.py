from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from pymongo import MongoClient
import psycopg2


def persist_data(data):
    conn = psycopg2.connect(host="postgresql",
                            database="testdb",
                            user="postgres",
                            password="example")

    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO price_history (product_alias, price, source)
                VALUES (%s, %s, %s);
            """, data)

    conn.close()


def get_prices(product_alias, targets, selectors):
    options = Options()
    options.headless = True
    service = Service('/app/geckodriver')
    driver = webdriver.Firefox(service=service, options=options)

    for target in targets:
        driver.get(target['url'])
        soup = BeautifulSoup(driver.page_source, features='html.parser')
        selector = next(
            (item for item in selectors if item["source"] == target['source']), None)

        price_tag = soup.find(attrs=selector['selector'])
        if not price_tag:
            print(
                f'Price not found! Skipping {product_alias} @ {target["source"]}')
            continue

        price = price_tag.text.replace('R$', '').replace(
            '.', '').replace(',', '.').strip()

        print(f"{target['source']} --- {price}")

        persist_data((product_alias, price, target['source']))

    driver.quit()


if __name__ == "__main__":
    client = MongoClient('mongodb://root:example@mongo:27017/',
                         serverSelectionTimeoutMS=3000)
    db = client.testdb
    products_db = db.products
    selectors_db = db.selectors

    selectors = list(selectors_db.find())

    for product in list(products_db.find()):
        print(f"Prices for {product['product_alias']}:")
        get_prices(product['product_alias'], product['targets'], selectors)
        print('\n=======================\n')
