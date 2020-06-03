from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from .models import  Item, Order, OrderItem
from django.utils import timezone


class HomeView(ListView):
    model = Item
    template_name = 'ecomm/home-page.html'
    context_object_name = "items"

def checkout_view(request):
    return render(request, "ecomm/checkout-page.html")

def product_view(request):
    return render(request, "ecomm/product-page.html")

class ItemDetailVieW(DetailView):
    model = Item
    template_name = "ecomm/product-page.html"

def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(item=item,
                                                 user=request.user,
                                                 ordered=False)

    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]

        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
        else:
            order.items.add(order_item)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)

    return redirect("ecomm:product-page", slug=slug)
