'''
Module providing all database app views.
'''

import json
from datetime import datetime
import pandas as pd
from django.shortcuts import render
from django.views.generic import ListView
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.core.files import File
from django.http.response import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from database.utils import generate_price_history_charts
from database.models import PriceHistory, Target, Product, Category, Frequencies, SelectorTypes
from database.scraping.utils import ScrapeStarter, running_commands, run_explore_command


class CategoryListView(LoginRequiredMixin, ListView):  # pylint: disable=too-many-ancestors
    ''' Class that provides the category list view '''

    template_name = 'database/categoryList.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.order_by('name').all()


class ProductListView(LoginRequiredMixin, ListView):  # pylint: disable=too-many-ancestors
    ''' Class that provides the product list view '''

    template_name = 'database/productList.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.order_by('name').all()


@login_required
def view_products_by_category(request, category_id):
    ''' Function that renders the products by category view '''

    products = Product.objects.filter(categories=category_id)

    return render(request, 'database/productList.html', {
        'products': products
    })


@login_required
@cache_page(86400, cache="filesystem")
def view_price_history(request, product_id):
    ''' Function that renders the price history view '''

    targets = Target.objects.filter(product_id=product_id)
    if not targets:
        return render(request, 'database/priceHistory.html')

    history = PriceHistory.objects.filter(
        target_id__in=[t.id for t in targets])
    if not history:
        return render(request, 'database/priceHistory.html')

    product_name = targets[0].product.name
    data_frame = pd.DataFrame([{
        'Alias': h.target.alias,
        'url': h.target.url,
        'Price': h.price,
        'Collection date': h.created_at,
    } for h in history])
    target_refs = json.loads(data_frame.filter(
        items=['url', 'Alias']).drop_duplicates().to_json(orient='records'))

    charts = generate_price_history_charts(data_frame, product_name)

    return render(request, 'database/priceHistory.html', {
        'product_name': product_name,
        'target_refs': target_refs,
        'charts': charts
    })


@ login_required
def view_download_database(request):
    ''' Function that renders the download database view '''

    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('index'))

    db_path = settings.DATABASES['default']['NAME']
    do_download = request.GET.get('do_download', False)

    if do_download and db_path:
        with File(open(db_path, "rb")) as db_file:
            new_name = f"{datetime.now()}{db_path}"
            response = HttpResponse(
                db_file, content_type='application/x-sqlite3')
            response['Content-Disposition'] = f'attachment; filename={new_name}'
            response['Content-Length'] = db_file.size

        return response

    return render(request, 'database/databaseDownload.html', {
        'db_path': db_path
    })


@ login_required
def view_scrape_command(request):
    ''' Function that renders the scrape command view '''

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


@ login_required
def view_explore_command(request):
    ''' Funtion that renders the explore command view '''

    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('index'))

    exploration_result = None
    targets = Target.objects.all()

    if request.method == 'POST':
        operation = request.POST['operation']

        if operation == "download-result":
            result_file = request.POST['result_file']

            with File(open(result_file, "rb")) as file:
                response = HttpResponse(file, content_type='text/html')
                response['Content-Disposition'] = f'attachment; filename={result_file}'
                response['Content-Length'] = file.size

            return response

        if operation == "explore-custom":
            url = request.POST['url']
            selector_type = request.POST['selector-type']
            selector = request.POST['selector']

            exploration_result = run_explore_command(
                url, selector_type, selector)

        if operation == "explore-known":
            target_id = int(request.POST["selected-target"])
            selected_target = targets.filter(id=target_id).get()

            if selected_target.selector:
                selector_type = selected_target.selector.selector_type
                selector = selected_target.selector.selector
            else:
                selector_type = selected_target.custom_selector_type
                selector = selected_target.custom_selector

            exploration_result = run_explore_command(
                selected_target.url, selector_type, selector)

    return render(request, 'database/exploreCommand.html', {
        'selector_types': SelectorTypes.choices,
        'exploration_result': exploration_result,
        'targets': targets
    })
