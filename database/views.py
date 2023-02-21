import json
import os
from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.core.files import File
from django.http.response import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.management import call_command
from datetime import datetime
from .utils import gen_color
from .models import PriceHistory, Target, Product, Category, Frequencies, SelectorTypes
from .scraping.utils import ScrapeStarter, running_commands
from prihud.settings import BASE_DIR


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


@login_required
def DownloadDatabaseView(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('index'))

    db_path = settings.DATABASES['default']['NAME']
    do_download = request.GET.get('do_download', False)

    if do_download and db_path:
        with File(open(db_path, "rb")) as db_file:
            new_name = f"{datetime.now()}{db_path}"
            response = HttpResponse(
                db_file, content_type='application/x-sqlite3')
            response['Content-Disposition'] = 'attachment; filename=%s' % new_name
            response['Content-Length'] = db_file.size

        return response

    return render(request, 'database/databaseDownload.html', {
        'db_path': db_path
    })


@login_required
def ScrapeCommandView(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('index'))

    if request.method == 'POST':
        frequency = request.POST['frequency']
        targets = request.POST.getlist('targets')
        starter = ScrapeStarter(frequency, targets)
        starter.start()

    return render(request, 'database/scrapeCommand.html', {
        'running_commands': running_commands,
        'frequencies': Frequencies.choices,
        'targets': Target.objects.values('id', 'alias', 'url').all()
    })


@login_required
def ExploreCommandView(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('index'))

    exploration_result = None

    if request.method == 'POST':
        operation = request.POST['operation']

        if operation == "download_result":
            result_file = request.POST['result_file']

            with File(open(result_file, "rb")) as file:
                response = HttpResponse(file, content_type='text/html')
                response['Content-Disposition'] = 'attachment; filename=%s' % result_file
                response['Content-Length'] = file.size

            return response

        if operation == "explore":
            url = request.POST['url']
            selector_type = request.POST['selector-type']
            selector = request.POST['selector']

            result = call_command(
                'explore', u=url, t=selector_type, s=selector)
            exploration_result = json.loads(result)

            file_url = url.replace(
                'https://', '').replace('/', '').replace(' ', '_')
            result_file = os.path.join(
                BASE_DIR, f'explore_{file_url}_{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}.html')
            exploration_result['result_file'] = result_file

            with open(result_file, 'w') as f:
                f.write(exploration_result['page_source'])

    return render(request, 'database/exploreCommand.html', {
        'selector_types': SelectorTypes.choices,
        'exploration_result': exploration_result
    })
