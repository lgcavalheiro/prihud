from .models import PriceHistory, Target, Product, Category
from django.shortcuts import render
from django.views.generic import ListView
from datetime import datetime
from .utils import gen_color


class CategoryListView(ListView):
    template_name = 'database/categoryList.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.order_by('name').all()


class ProductListView(ListView):
    template_name = 'database/productList.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.order_by('name').all()


def ProductsByCategoryView(request, category_id):
    products = Product.objects.filter(categories=category_id)

    return render(request, 'database/productList.html', {
        'products': products
    })


def PriceHistoryView(request, product_id):
    targets = Target.objects.filter(product_id=product_id)
    if not targets:
        return render(request, 'database/priceHistory.html')

    history = PriceHistory.objects.filter(
        target_id__in=[t.id for t in targets])
    if not history:
        return render(request, 'database/priceHistory.html')

    partial_data = {}
    labels = []
    for h in history:
        if h.target.url not in partial_data:
            partial_data[h.target.url] = {
                'label': h.target.alias or h.target.url,
                'data': [],
                'borderColor': gen_color(),
                'tension': 0.1,
            }
        partial_data[h.target.url]['data'].append(h.price)
        labels.append(h.created_at.strftime("%m/%d/%y %H:%M"))

    if len(partial_data) > 1:
        labels = list(set(labels))
        labels.sort()

    return render(request, 'database/priceHistory.html', {
        'labels': labels,
        'product_name': targets[0].product.name,
        'datasets': list(partial_data.values()),
        'target_refs': [{'url': target.url, 'alias': target.alias} for target in targets]
    })
