from .views import item_list

from django.urls import path
app_name = 'ecomm'

urlpatterns = [
    path('', item_list, name='item_list')
]