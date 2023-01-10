from django.test import TestCase
from django.urls import reverse
from .utils import gen_color, rand
from .models import Category, Product, Target, PriceHistory


def create_category():
    return Category.objects.create(name="Test category")


def create_product():
    test_product = Product.objects.create(name="Test product")
    test_product.categories.set([create_category()])
    return test_product


def create_target():
    return Target.objects.create(url="test_url",
                                 selector_type="css",
                                 selector=".test", product=create_product())


def create_price_history():
    return PriceHistory.objects.create(price=2.5, target=create_target())


class UtilsTest(TestCase):
    def test_generates_number_between_zero_and_255(self):
        num = rand()
        self.assertGreaterEqual(num, 0)
        self.assertLessEqual(num, 255)

    def test_generates_valid_color(self):
        color = gen_color()
        self.assertIs(len(color), 7)


class CategoryListViewTest(TestCase):
    def test_show_message_when_no_categories(self):
        response = self.client.get(reverse('database:categoryList'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No categories found")
        self.assertQuerysetEqual(response.context['categories'], [])

    def test_show_category_list(self):
        test_category = create_category()
        response = self.client.get(reverse('database:categoryList'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, test_category.name)
        self.assertQuerysetEqual(
            response.context['categories'], [test_category])


class ProductListViewTest(TestCase):
    def test_show_message_when_no_products(self):
        response = self.client.get(reverse('database:productList'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No products found for this category :(")
        self.assertQuerysetEqual(response.context['products'], [])

    def test_show_product_list(self):
        test_product = create_product()
        response = self.client.get(reverse('database:productList'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, test_product.name)
        self.assertQuerysetEqual(response.context['products'], [test_product])


class ProductsByCategoryViewTest(TestCase):
    def test_show_message_when_no_category_found(self):
        url = reverse('database:productsByCategoryView', args=(111,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No products found for this category :(")

    def test_show_products_by_category(self):
        test_product = create_product()
        url = reverse('database:productsByCategoryView', args=(1,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, test_product.name)
        self.assertQuerysetEqual(response.context['products'], [test_product])


class PriceHistoryViewTest(TestCase):
    def test_show_message_when_no_price_history(self):
        url = reverse('database:priceHistory', args=(111,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "No price history found for this product")

    def test_show_price_history(self):
        test_price_history = create_price_history()
        url = reverse('database:priceHistory', args=(1,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, test_price_history.target.product.name)
        self.assertGreater(len(response.context['datasets']), 0)
