from django.shortcuts import render
from .models import  Item


def home_page(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, "ecomm/home-page.html", context)


def checkout_view(request):
    return render(request, "ecomm/checkout-page.html")

def product_view(request):
    return render(request, "ecomm/product-page.html")