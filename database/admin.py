from django.contrib import admin

from .models import Category, Target, Product, PriceHistory

admin.site.register(Category)
admin.site.register(Target)
admin.site.register(Product)
admin.site.register(PriceHistory)
