from django.urls import path

from . import views

app_name = 'database'
urlpatterns = [
    path('categories/', views.CategoryListView.as_view(), name='categoryList'),
    path('categories/<int:category_id>/',
         views.ProductsByCategoryView, name='productsByCategoryView'),
    path('products/', views.ProductListView.as_view(), name='productList'),
    path('history/<int:product_id>/', views.PriceHistoryView, name='priceHistory'),
    path('admin/db-download/', views.DownloadDatabaseView, name="downloadDatabase")
]
