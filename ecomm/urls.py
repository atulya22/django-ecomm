from .views import home_page, checkout_view, product_view

from django.urls import path
app_name = 'ecomm'

urlpatterns = [
    path('', home_page, name='home-page'),
    path('checkout/', checkout_view, name='checkout-page'),
    path('products/', product_view, name='product-page')

]