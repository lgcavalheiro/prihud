from django.utils.timezone import now
from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=128, null=False)
    created_at = models.DateTimeField('created_at', default=now)
    updated_at = models.DateTimeField('updated_at', default=now)

    def __str__(self):
        return self.name

    # def get_absolute_url(self):
    #     return reverse('database:index')


class Product(models.Model):
    name = models.CharField(max_length=128, null=False)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField('created_at', default=now)
    updated_at = models.DateTimeField('updated_at', default=now)

    def __str__(self):
        return self.name


class Target(models.Model):
    url = models.CharField(max_length=256, null=False)
    selector_type = models.CharField(max_length=8, null=False)
    selector = models.CharField(max_length=256, null=False)
    product = models.ForeignKey(
        Product, on_delete=models.DO_NOTHING, null=False)
    created_at = models.DateTimeField('created_at', default=now)
    updated_at = models.DateTimeField('updated_at', default=now)

    def __str__(self):
        return f'{self.url} - {self.selector_type} - {self.selector}'


class PriceHistory(models.Model):
    price = models.FloatField(null=False)
    target = models.ForeignKey(Target, on_delete=models.DO_NOTHING, null=False)
    created_at = models.DateTimeField('created_at', default=now)
    updated_at = models.DateTimeField('updated_at', default=now)

    def __str__(self):
        return f'{self.price} - {self.target}'
