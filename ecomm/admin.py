from django.contrib import admin
from .models import Item, OrderItem, Order, Payment, Coupon, Refund


def approve_refund(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


approve_refund.short_description = 'Approve Requested Refund'

# Register your models here.
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'ordered', 'being_delivered',
                    'received', 'refund_requested', 'refund_granted',
                    'user', 'billing_address', 'payment', 'coupon']

    list_display_links = ['billing_address', 'payment', 'coupon']

    list_filter = ['user', 'ordered', 'being_delivered',
                    'received', 'refund_requested', 'refund_granted']

    search_fields = [
        'user__username',
        'ref_code'
    ]

    actions = [approve_refund]

admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)