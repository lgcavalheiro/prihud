# pylint: disable=missing-docstring

from io import StringIO
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test.client import Client
from django.core.management import call_command
from django.test import tag
from database import models
from database.scraping.impl.scraping_job import ScrapingJob

DEFAULT_USER = "testuser"
DEFAULT_EMAIL = "test@user.local"
DEFAULT_PASS = "1test2password3"
DEFAULT_URL = "test_url"

ADMIN_USER = "admin"
ADMIN_PASS = "adm123"
ADMIN_EMAIL = "admin@user.local"


def create_category():
    return models.Category.objects.create(name="Test category")


def create_product():
    test_product = models.Product.objects.create(name="Test product")
    test_product.categories.set([create_category()])
    return test_product


def create_target(url=None):
    url = url if url else DEFAULT_URL
    custom_selector = ".product-price-current > span:nth-child(1)"
    return models.Target.objects.create(url=url,
                                        custom_selector_type=models.SelectorTypes.CSS,
                                        custom_selector=custom_selector,
                                        product=create_product())


def create_price_history():
    return models.PriceHistory.objects.create(price=2.5, target=create_target())


def run_scrape_command(use_ids=False):
    out = StringIO()
    if use_ids:
        call_command('scrape', i=[1], stdout=out, stderr=out)
    else:
        call_command('scrape', f='D', stdout=out, stderr=out)
    return out


def setup_login(self):
    self.client = Client()
    self.user = get_user_model().objects.create_user(
        DEFAULT_USER, DEFAULT_EMAIL, DEFAULT_PASS)
    self.admin = get_user_model().objects.create_superuser(
        ADMIN_USER, ADMIN_EMAIL, ADMIN_PASS)


def do_login(self, as_admin=False):
    if as_admin:
        self.client.login(username=ADMIN_USER, password=ADMIN_PASS)
    else:
        self.client.login(username=DEFAULT_USER, password=DEFAULT_PASS)


@tag('view')
class CategoryListViewTest(TestCase):
    def setUp(self):
        setup_login(self)

    def test_show_message_when_no_categories(self):
        do_login(self)
        response = self.client.get(reverse('database:categoryList'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No categories found")
        self.assertQuerysetEqual(response.context['categories'], [])

    def test_show_category_list(self):
        do_login(self)
        test_category = create_category()
        response = self.client.get(reverse('database:categoryList'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, test_category.name)
        self.assertQuerysetEqual(
            response.context['categories'], [test_category])


@tag('view')
class ProductListViewTest(TestCase):
    def setUp(self):
        setup_login(self)

    def test_show_message_when_no_products(self):
        do_login(self)
        response = self.client.get(reverse('database:productList'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No products found for this category :(")
        self.assertQuerysetEqual(response.context['products'], [])

    def test_show_product_list(self):
        do_login(self)
        test_product = create_product()
        response = self.client.get(reverse('database:productList'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, test_product.name)
        self.assertQuerysetEqual(response.context['products'], [test_product])


@tag('view')
class ProductsByCategoryViewTest(TestCase):
    def setUp(self):
        setup_login(self)

    def test_show_message_when_no_category_found(self):
        do_login(self)
        url = reverse('database:productsByCategoryView', args=(111,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No products found for this category :(")

    def test_show_products_by_category(self):
        do_login(self)
        test_product = create_product()
        url = reverse('database:productsByCategoryView', args=(1,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, test_product.name)
        self.assertQuerysetEqual(response.context['products'], [test_product])


@tag('view')
class PriceHistoryViewTest(TestCase):
    def setUp(self):
        setup_login(self)

    def test_show_message_when_no_price_history(self):
        do_login(self)
        url = reverse('database:priceHistory', args=(111,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "No price history found for this product")

    def test_show_price_history(self):
        do_login(self)
        test_price_history = create_price_history()
        url = reverse('database:priceHistory', args=(1,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, test_price_history.target.product.name)
        self.assertGreater(len(response.context['target_refs']), 0)


@tag('view')
class DownloadDatabaseViewTest(TestCase):
    def setUp(self):
        setup_login(self)

    def test_show_download_link(self):
        do_login(self, as_admin=True)
        url = reverse('database:downloadDatabase')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Download database file")

    def test_show_download_link_redirect(self):
        do_login(self)
        url = reverse('database:downloadDatabase')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)


@tag('command')
class ScrapeCommandTest(TestCase):
    def test_run_scrape_no_targets(self):
        out = run_scrape_command()
        self.assertIn("Found no targets", out.getvalue())

    def test_run_scrape(self):
        create_target(
            url="https://pt.aliexpress.com/item/4000440445220.html")
        out = run_scrape_command()
        self.assertIn("Results: 1/1 successes", out.getvalue())

    def test_run_scrape_failed(self):
        create_target()
        out = run_scrape_command()
        self.assertIn("Had 1 failures", out.getvalue())
        self.assertIn("PriceNotFoundException", out.getvalue())
        self.assertIn(DEFAULT_URL, out.getvalue())

    def test_use_ids_for_scraping(self):
        create_target(url="https://pt.aliexpress.com/item/4000440445220.html")
        create_target(url="https://pt.aliexpress.com/item/123123123123.html")
        out = run_scrape_command(use_ids=True)
        self.assertIn("Results: 1/1 successes", out.getvalue())


@tag('model')
class CategoryModelTest(TestCase):
    def test_can_str(self):
        category = create_category()
        self.assertEqual(category.name, str(category))


@tag('model')
class ProductModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.history = create_price_history()
        cls.product = cls.history.target.product

    def test_can_str(self):
        self.assertEqual(self.product.name, str(self.product))

    def test_get_price_history(self):
        price_history = self.product.get_price_history()
        self.assertEqual(self.history, price_history[0])

    def test_min_max_prices(self):
        prices = self.product.get_min_max_prices()
        self.assertEqual(self.history.price, prices['price__min'])
        self.assertEqual(self.history.price, prices['price__max'])

    def test_get_cheapest(self):
        cheapest = self.product.get_cheapest()
        self.assertEqual(self.history, cheapest)


@tag('model')
class TargetModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.history = create_price_history()
        cls.target = cls.history.target

    def test_can_str(self):
        self.assertEqual(self.target.url, str(self.target))

    def test_can_str_with_alias(self):
        self.target.alias = "alias-test"
        self.assertEqual(self.target.alias, str(self.target))

    def test_min_max_price(self):
        price_history = self.target.min_max_price()
        self.assertEqual(self.history.price, price_history['price__min'])
        self.assertEqual(self.history.price, price_history['price__max'])

    def test_get_store_name_from_url_empty(self):
        store_name = self.target.get_store_name_from_url()
        self.assertEqual('', store_name)

    def test_get_store_name_from_url(self):
        self.target.url = "https://www.searx.space"
        store_name = self.target.get_store_name_from_url()
        self.assertEqual('searx', store_name)

    def test_get_recent_price_history(self):
        recent = self.target.get_recent_price_history()
        self.assertEqual(self.history, recent)

    def test_is_available(self):
        is_available = self.target.is_available()
        self.assertTrue(is_available)


@tag('model')
class PriceHistoryModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.history = create_price_history()

    def test_can_str(self):
        self.assertEqual(
            ' - '.join([
                str(self.history.price),
                str(self.history.target),
                str(self.history.created_at)
            ]),
            str(self.history))


@tag('scraping')
class ScrapingJobTest(TestCase):
    def setUp(self):
        self.history = create_price_history()
        cookie = models.Cookie(url="https://pt.aliexpress.com", name="test-cookie",
                               value="test-val", path="/", domain=".aliexpress.com")
        cookie.save()
        self.job = ScrapingJob([self.history.target])

    def test_can_use_cookies(self):
        self.assertEqual(
            "test-cookie", self.job.scraper.driver.get_cookie("test-cookie")['name'])

    def test_can_save_target_status(self):
        self.job.save_target_status(
            self.history.target, models.Statuses.OUT_OF_STOCK)
        self.assertEqual(self.history.target.status,
                         models.Statuses.OUT_OF_STOCK)


@tag('model')
class CookieModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cookie = models.Cookie(url="https://pt.aliexpress.com", name="test-cookie",
                                   value="test-val", path="/", domain=".aliexpress.com")

    def test_can_str(self):
        self.assertEqual(
            f'{self.cookie.url} - {self.cookie.name}', str(self.cookie))


@tag('model')
class DefaultSelectorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.selector = models.DefaultSelector(
            name="test-selector", selector_type=models.SelectorTypes.CSS, selector=".test")

    def test_can_str(self):
        self.assertEqual(self.selector.name, str(self.selector))


@tag('view')
class ScrapeCommandViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        setup_login(cls)

    def test_redirects_non_admins(self):
        do_login(self)
        response = self.client.get(reverse('database:scrapeCommand'))
        self.assertEqual(response.status_code, 302)

    def test_can_run_scrape_command_from_view(self):
        do_login(self, as_admin=True)
        response = self.client.post(reverse('database:scrapeCommand'), data={
            'targets': [1],
            'frequency': ''
        })
        self.assertEqual(response.status_code, 200)


@tag('view')
class ExploreCommandViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        setup_login(cls)

    def test_redirects_non_admins(self):
        do_login(self)
        response = self.client.get(reverse('database:exploreCommand'))
        self.assertEqual(response.status_code, 302)

    def test_can_run_explore_command_from_view_and_download_result(self):
        do_login(self, as_admin=True)
        response = self.client.post(reverse('database:exploreCommand'), data={
            'operation': 'explore-custom',
            'url': 'https://pt.aliexpress.com/item/1005003603757192.html',
            'selector-type': models.SelectorTypes.CSS,
            'selector': '.product-price-current > span:nth-child(1)'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Status:")
        self.assertContains(response, "Download result")

        result_file = response.context[-1]["exploration_result"]["result_file"]
        response = self.client.post(reverse('database:exploreCommand'), data={
            'operation': 'download-result',
            'result_file': result_file
        })
        content_disposition = response.get('Content-Disposition')
        self.assertEqual(content_disposition,
                         f'attachment; filename={result_file}')
