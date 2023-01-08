from .models import PriceHistory, Target, Product
from django.shortcuts import render
from datetime import datetime


def PriceHistoryView(request, product_id):
    product = Product.objects.filter(id=product_id).first()
    target = Target.objects.filter(product=product).first()
    history = PriceHistory.objects.filter(target=target).all()

    data = []
    labels = []
    for h in history:
        data.append(h.price)
        labels.append(h.created_at.strftime("%m/%d/%Y, %H:%M:%S"))

    return render(request, 'database/priceHistory.html', {
        'data': data,
        'labels': labels,
        'product_name': product.name,
        'target_url': target.url,
    })
