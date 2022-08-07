from django.contrib import admin
from .models import Payment, Order, Order_product


# Register your models here.

class OrderProductInline(admin.TabularInline):
    model = Order_product
    extra = 0
    readonly_fields = ('payment', 'user', 'product', 'variations', 'quantity', 'product_price', 'is_ordered')


class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'phone', 'email', 'city', 'order_total', 'tax', 'status', 'is_ordered',
                    'created_at', ]
    list_filter = ['is_ordered', 'status', ]
    search_fields = ['order_number', 'full_name', 'phone', 'email', 'is_ordered', 'city', ]
    list_per_page = 20
    inlines = [OrderProductInline]


admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(Order_product)
