from .views import (ItemDetailVieW,
                    HomeView,
                    OrderSummaryView,
                    add_to_cart,
                    AddCoupon,
                    remove_from_cart,
                    remove_single_item_from_cart,
                    CheckoutView,
                    PaymentView,
                    RequestRefundView)

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static


app_name = 'ecomm'

urlpatterns = [
    path('', HomeView.as_view(), name='home-page'),
    path('checkout/', CheckoutView.as_view(), name='checkout-page'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('product/<slug>/', ItemDetailVieW.as_view(), name='product-page'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart, name='remove-single-item-from-cart'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('add-coupon/', AddCoupon.as_view(), name='add-coupon'),
    path('refund/', RequestRefundView.as_view(), name='refund'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)