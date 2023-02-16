from threading import Thread
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
from .models import PriceHistory, Target, Product, Category, Frequencies


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


running_commands = []


class CommandStarter(Thread):
    frequency = None
    targets = []

    def __init__(self, frequency, targets):
        super(CommandStarter, self).__init__()
        self.frequency = frequency
        self.targets = targets
        running_commands.append(self)

    def run(self):
        if self.frequency:
            call_command('scrape', f=self.frequency)
        elif len(self.targets) > 0:
            call_command('scrape', i=self.targets)
        running_commands.remove(self)


@login_required
def CommandsView(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('index'))

    if request.method == 'POST':
        frequency = request.POST['frequency']
        targets = request.POST.getlist('targets')
        starter = CommandStarter(frequency, targets)
        starter.start()

    return render(request, 'database/commands.html', {
        'running_commands': running_commands,
        'frequencies': Frequencies.choices,
        'targets': Target.objects.values('id', 'alias', 'url').all()
    })
