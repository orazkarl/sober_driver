from django.contrib import admin
from .models import City, Order, OfferOrder, Review
from django.db.models import Count
# admin.site.register(Review)
import datetime
@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name']

    # def get_count_orders(self, obj):
    #     return f"{Order.objects.filter(city=obj, status='finished').count()}"
    #
    # get_count_orders.short_description = 'Количество заказов'
    #
    # def get_income_orders(self, obj):
    #     return f"{Order.objects.filter(city=obj, status='finished').count() * obj.overpayment}"
    #
    # get_income_orders.short_description = 'Доход от заказов'


class OrderDateFilter(admin.SimpleListFilter):
    title = 'Фильтр по дате'
    parameter_name = 'date'

    def lookups(self, request, model_admin):
        return (
            ('день', 'День'),
            ('неделя', 'Неделя'),
            ('месяц', 'Месяц'),
            ('год', 'Год'),

        )

    def queryset(self, request, queryset):
        if self.value() == 'день':
            return queryset.filter(created__gte=datetime.datetime.today() - datetime.timedelta(days=1))
        if self.value() == 'неделя':
            return queryset.filter(created__gte=datetime.datetime.today() - datetime.timedelta(days=7))
        if self.value() == 'месяц':
            return queryset.filter(created__gte=datetime.datetime.today() - datetime.timedelta(days=30))
        if self.value() == 'год':
            return queryset.filter(created__gte=datetime.datetime.today() - datetime.timedelta(days=365))



@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'city', 'from_address', 'to_address', 'status', 'created', 'selected_driver']
    list_filter = ['status', 'city', OrderDateFilter]
    fieldsets = (
        (None,{'fields': ('phone_number', 'city', 'from_address', 'to_address', 'status', 'created', 'selected_driver')}),
    )
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
