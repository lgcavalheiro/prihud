from django.urls import path

from . import views

app_name = 'database'
urlpatterns = [
    path('history/<int:product_id>/', views.PriceHistoryView, name='priceHistory')
]
