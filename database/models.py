from django.utils.timezone import now
from django.db import models
from django.urls import reverse
from django.db.models import Min, Max
from datetime import datetime


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


class Target(models.Model):
    alias = models.CharField(max_length=128, null=True)
    url = models.CharField(max_length=256)
    selector_type = models.CharField(max_length=8)
    selector = models.CharField(max_length=256)
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


class PriceHistory(models.Model):
    price = models.FloatField()
    target = models.ForeignKey(Target, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField('created_at', default=now)
    updated_at = models.DateTimeField('updated_at', default=now)

    def __str__(self):
        return f'{self.price} - {self.target} - {self.created_at}'
