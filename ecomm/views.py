from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import ListView, DetailView, View
from .models import  Item, Order, OrderItem, BillingAddress, Payment, Coupon, Refund
from django.utils import timezone
from django.contrib import messages
from .forms import CheckoutForm, CouponForm, RefundForm
import stripe
import random
import string

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=30))


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


class CheckoutView(View):

    def get(self, *args, **kwargs):
        form = CheckoutForm()
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }
            return render(self.request, "ecomm/checkout-page.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            redirect("ecomm:checkout-page.html")


    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                # same_shipping_address = form.cleaned_data.get('same_shipping_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_info = form.cleaned_data.get('payment_option')

                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip,
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()

                if payment_info == 'S':
                    return redirect('ecomm:payment', payment_option='stripe')
                elif payment_info == 'P':
                    return redirect('ecomm:payment', payment_option='paypal')
                else:
                    messages.warning(self.request,"Invalid payment option selected")
                    return redirect('ecomm:checkout-page')

        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect('ecomm:order-summary')

        messages.warning(self.request, "failed to checkout")
        return redirect('ecomm:checkout-page')


class PaymentView(View):
    def get(self, *args, **kwargs):
        # order info
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False
            }
        else:
            messages.warning(self.request, "You have not added a billing address")
            return redirect("ecomm:order-summary")

        return render(self.request, "ecomm/payment.html", context)

    def post(self, *args, **kwargs):
        token = self.request.POST.get('stripeToken')
        print(self.request.POST)
        order = Order.objects.get(user=self.request.user, ordered=False)
        amount = int(order.get_total() * 100)
        try:
            charge = stripe.Charge.create(
                api_key=settings.STRIPE_SECRET_KEY,
                amount=amount,
                currency="USD",
                source=token,
             )
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()

            order.ordered = True
            order.payment = payment
            order.ref_code = create_ref_code()
            order.save()

            messages.success(self.request, "Your order was successful")
            return redirect("/")
        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            messages.error(self.request, f"{err.get('message')}")
            return redirect("/")
        except Exception as e:

            messages.error(self.request, str(e))
            return redirect("/")



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


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This is not a valid coupon")


class AddCoupon(View):
    def post(self, *args, **kwargs):
        if self.request.method == 'POST':
            form = CouponForm(self.request.POST or None)
            if form.is_valid():
                try:
                    code = form.cleaned_data.get('code')
                    order = Order.objects.get(user=self.request.user, ordered=False)
                    order.coupon = get_coupon(self.request, code)
                    order.save()
                    messages.success(request, "Successfully added coupon")
                    return redirect("ecomm:checkout-page")
                except ObjectDoesNotExist:
                    messages.info("You do not have an active order")
                    return redirect("ecomm:checkout-page")


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "ecomm/refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)

        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')

            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                refund = Refund(order=order, reason=message, email=email)
                refund.save()

                messages.info(self.request, "Your request was received")
                return redirect("ecomm:refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist")
                return redirect("ecomm:refund")

