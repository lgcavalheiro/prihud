from django.utils.timezone import now
from django.db import models
from django.urls import reverse
from django.db.models import Min, Max
from django.utils.translation import gettext_lazy as _
from selenium.webdriver.common.by import By
from datetime import datetime


class Statuses(models.TextChoices):
    SUCCESS = 'S', _('Success')
    OUT_OF_STOCK = 'O', _('Out of stock')
    NO_SELECTOR = 'N', _('No selector set')
    PRICE_NOT_FOUND = 'P', _('Price not found')
    CACHED = "C", _("Cached")
    UNDEFINED = 'U', _('Undefined status')


class Frequencies(models.TextChoices):
    FOUR_TIMES = 'F', _('Four times a day')
    TWO_TIMES = 'T', _('Twice a day')
    DAILY = 'D', _('Daily')
    WEEKLY = 'W', _('Weekly')


class SelectorTypes(models.TextChoices):
    CSS = By.CSS_SELECTOR
    XPATH = By.XPATH
    TAG = By.TAG_NAME
    CLASS = By.CLASS_NAME


class Category(models.Model):
    name = models.CharField(max_length=128)
    created_at = models.DateTimeField('created_at', default=now)
    updated_at = models.DateTimeField('updated_at', default=now)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=128)
    categories = models.ManyToManyField(Category)
    created_at = models.DateTimeField('created_at', default=now)
    updated_at = models.DateTimeField('updated_at', default=now)

    def __str__(self):
        return self.name

    def get_price_history(self):
        targets = Target.objects.filter(product_id=self.id).all()
        return PriceHistory.objects.filter(target_id__in=[t.id for t in targets]).order_by('-created_at').all()

    def get_min_max_prices(self):
        targets = Target.objects.filter(product_id=self.id).all()
        return PriceHistory.objects.filter(target_id__in=[t.id for t in targets]).aggregate(Min('price'), Max('price'))

    def get_cheapest(self):
        targets = Target.objects.filter(product_id=self.id).all()
        return PriceHistory.objects.filter(target_id__in=[t.id for t in targets]).annotate(Min('price')).order_by('price')[0]


class DefaultSelector(models.Model):
    name = models.CharField(max_length=64)
    selector_type = models.CharField(
        max_length=16, choices=SelectorTypes.choices)
    selector = models.CharField(max_length=256)
    created_at = models.DateTimeField('created_at', default=now)
    updated_at = models.DateTimeField('updated_at', default=now)

    def __str__(self):
        return self.name


class Target(models.Model):
    alias = models.CharField(max_length=128, null=True)
    url = models.CharField(max_length=256)
    selector = models.ForeignKey(
        DefaultSelector, on_delete=models.DO_NOTHING, null=True)
    custom_selector_type = models.CharField(
        max_length=16, choices=SelectorTypes.choices, null=True)
    custom_selector = models.CharField(max_length=256, null=True)
    status = models.CharField(
        max_length=1, null=True, choices=Statuses.choices, default=Statuses.SUCCESS)
    frequency = models.CharField(
        max_length=1, choices=Frequencies.choices, default=Frequencies.DAILY)
    product = models.ForeignKey(
        Product, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField('created_at', default=now)
    updated_at = models.DateTimeField('updated_at', default=now)

    def __str__(self):
        return self.alias or self.url

    def min_max_price(self):
        return PriceHistory.objects.filter(target_id=self.id).aggregate(Min('price'), Max('price'))

    def get_store_name_from_url(self):
        splitted = self.url.split('.')
        return splitted[1] if len(splitted) > 1 else ''

    def get_recent_price_history(self):
        return PriceHistory.objects.filter(target_id=self.id).order_by('-created_at').first()

    def is_available(self):
        return self.status in [Statuses.SUCCESS, Statuses.CACHED]


class PriceHistory(models.Model):
    price = models.FloatField()
    target = models.ForeignKey(Target, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField('created_at', default=now)
    updated_at = models.DateTimeField('updated_at', default=now)

    def __str__(self):
        return f'{self.price} - {self.target} - {self.created_at}'


class Cookie(models.Model):
    url = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    value = models.TextField()
    path = models.CharField(max_length=256, null=True, default='/')
    domain = models.CharField(max_length=256)
    created_at = models.DateTimeField('created_at', default=now)
    updated_at = models.DateTimeField('updated_at', default=now)

    def __str__(self):
        return f'{self.url} - {self.name}'

    def get_all_grouped():
        cookies = Cookie.objects.all()
        grouped = {}
        for cookie in cookies:
            if cookie.url not in grouped:
                grouped[cookie.url] = []
            grouped[cookie.url].append(cookie)
        return grouped

    def get_parsed(self):
        return {
            'name': self.name,
            'value': self.value,
            'path': self.path,
            'domain': self.domain
        }
