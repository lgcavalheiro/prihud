''' Module providing admin configurations for the database module '''

from django.contrib import admin

from .models import Category, Target, Product, PriceHistory, Cookie, DefaultSelector

admin.site.register(Category)
admin.site.register(Target)
admin.site.register(Product)
admin.site.register(PriceHistory)
admin.site.register(Cookie)
admin.site.register(DefaultSelector)
