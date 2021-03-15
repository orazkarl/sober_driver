from django.contrib import admin
from .models import City, Order, OfferOrder
from django.db.models import Count


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_count_orders', 'get_income_orders']

    def get_count_orders(self, obj):
        return f"{Order.objects.filter(city=obj, status='finished').count()}"

    get_count_orders.short_description = 'Количество заказов'

    def get_income_orders(self, obj):
        return f"{Order.objects.filter(city=obj, status='finished').count() * obj.overpayment}"

    get_income_orders.short_description = 'Доход от заказов'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'city', 'from_address', 'to_address', 'status', 'created', 'selected_driver']
