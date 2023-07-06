from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from database.models import PriceHistory, Target, Product
from django.db.models import Min, Max


def __handle_post(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if not user:
        return render(request, 'login.html', {
            'login_failed': True
        })
    login(request, user)
    return HttpResponseRedirect(reverse('index'))


def __handle_get(request):
    if not request.user.is_authenticated:
        return render(request, 'login.html')
    return HttpResponseRedirect(reverse('index'))


def LoginView(request):
    if request.method == 'GET':
        return __handle_get(request)
    elif request.method == 'POST':
        return __handle_post(request)
    else:
        return render(request, 'login.html')


def Logout(request):
    logout(request)
    return render(request, 'login.html')


def Index(request):
    products = Product.objects.order_by('created_at').all()
    latest = []
    [latest.extend(p.get_price_history()[:1]) for p in products]

    targets = Target.objects.all()
    inactive = list(filter(lambda t: not t.is_available(), targets))

    return render(request, 'index.html', {
        'latest': latest,
        'inactive': inactive
    })
