from .views import checkout_view, ItemDetailVieW, HomeView, add_to_cart

from django.urls import path
app_name = 'ecomm'

urlpatterns = [
    path('', HomeView.as_view(), name='home-page'),
    path('checkout/', checkout_view, name='checkout-page'),
    path('product/<slug>/', ItemDetailVieW.as_view(), name='product-page'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart')

]