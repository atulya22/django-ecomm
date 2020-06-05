from django import template
from ecomm.models import Order

register = template.Library()


@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        print("Here Now")
        qs = Order.objects.filter(user=user, ordered=False)
        if qs.exists():
            print(f"{qs}")
            return qs[0].items.count()
    return 0