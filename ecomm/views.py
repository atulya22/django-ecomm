from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import ListView, DetailView, View
from .models import  Item, Order, OrderItem
from django.utils import timezone
from django.contrib import messages

class HomeView(ListView):
    model = Item
    template_name = 'ecomm/home-page.html'
    paginate_by = 10
    context_object_name = "items"


class OrderSummaryView(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect('/')
        return render(self.request, 'ecomm/order-summary.html', context)

def checkout_view(request):
    return render(request, "ecomm/checkout-page.html")

def product_view(request):
    return render(request, "ecomm/product-page.html")

class ItemDetailVieW(DetailView):
    model = Item
    template_name = "ecomm/product-page.html"

@login_required
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
            messages.info(request, "This item quantity was updated.")

        else:
            messages.info(request, "This item was added to your cart.")
            order.items.add(order_item)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)

    return redirect("ecomm:order-summary")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    print("Inside Remove Cart")
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item,
                                                  user=request.user,
                                                  ordered=False)[0]
            order.items.remove(order_item)
            messages.info(request, "This item was removed from your cart.")
            return redirect("ecomm:order-summary")
        else:
            messages.info(request, "This item was not in your cart.")
            return redirect("ecomm:product-page", slug=slug)
    else:
        messages.info(request, "You do not have an active order.")
        return redirect("ecomm:product-page", slug=slug)


def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )

    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item,
                                                  user=request.user,
                                                  ordered=False)[0]

            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                print(f"Type: {type(order.items)}")
                order.items.remove(order_item)

            messages.info(request, "This item quantity was updated.")
            return redirect("ecomm:order-summary")
        else:
            messages.info(request, "This item was not in your cart.")
            return redirect("ecomm:product-page", slug=slug)
    else:
        messages.info(request, "You do not have an active order.")
        return redirect("ecomm:product-page", slug=slug)

