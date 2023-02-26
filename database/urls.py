''' 
Module that provides all urls for database app.
'''

from django.urls import path
from database import views

app_name = 'database'
urlpatterns = [
    path('categories/', views.CategoryListView.as_view(), name='categoryList'),
    path('products/', views.ProductListView.as_view(), name='productList'),
    path('categories/<int:category_id>/',
         views.view_products_by_category, name='productsByCategoryView'),
    path('history/<int:product_id>/',
         views.view_price_history, name='priceHistory'),
    path('admin/db-download/', views.view_download_database,
         name="downloadDatabase"),
    path('admin/scrape', views.view_scrape_command, name="scrapeCommand"),
    path('admin/explore', views.view_explore_command, name="exploreCommand")
]
