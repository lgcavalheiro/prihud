from .models import PriceHistory, Target, Product, Category
from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime
from .utils import gen_color


class CategoryListView(LoginRequiredMixin, ListView):
    template_name = 'database/categoryList.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.order_by('name').all()


class ProductListView(LoginRequiredMixin, ListView):
    template_name = 'database/productList.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.order_by('name').all()


@login_required
def ProductsByCategoryView(request, category_id):
    products = Product.objects.filter(categories=category_id)

    return render(request, 'database/productList.html', {
        'products': products
    })


@login_required
def PriceHistoryView(request, product_id):
    targets = Target.objects.filter(product_id=product_id)
    if not targets:
        return render(request, 'database/priceHistory.html')

    history = PriceHistory.objects.filter(
        target_id__in=[t.id for t in targets])
    if not history:
        return render(request, 'database/priceHistory.html')

    labels = []
    partial_data = {}
    for h in history:
        if h.target.url not in partial_data:
            partial_data[h.target.url] = {
                'label': h.target.alias or h.target.url,
                'data': [],
                'borderColor': gen_color(),
            }
        price_date = h.created_at.strftime("%m/%d/%y %H:%M")
        partial_data[h.target.url]['data'].append(
            {'x': price_date, 'y': h.price})
        labels.append(price_date)

    return render(request, 'database/priceHistory.html', {
        'labels': sorted(set(labels)),
        'datasets': list(partial_data.values()),
        'product_name': targets[0].product.name,
        'target_refs': [{'url': target.url, 'alias': target.alias} for target in targets]
    })
