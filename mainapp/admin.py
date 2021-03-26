from django.contrib import admin
from .models import City, Order, OfferOrder, Review, Overpayment
from django.db.models import Count
# admin.site.register(Review)
from django.contrib.sites.models import  Site
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


class OrderMonthFilter(admin.SimpleListFilter):
    title = 'Фильтр по месяцам "'+ str(datetime.datetime.now().year)+  ' год"'
    parameter_name = 'month'

    def lookups(self, request, model_admin):
        return (
            ('1', 'Январь'),
            ('2', 'Февраль'),
            ('3', 'Март'),
            ('4', 'Апрель'),
            ('5', 'Май'),
            ('6', 'Июнь'),
            ('7', 'Июль'),
            ('8', 'Август'),
            ('9', 'Сентябрь'),
            ('10', 'Октябрь'),
            ('11', 'Ноябрь'),
            ('12', 'Декабрь'),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(created__month='1', created__year=datetime.datetime.now().year)
        if self.value() == '2':
            return queryset.filter(created__month='2', created__year=datetime.datetime.now().year)
        if self.value() == '3':
            return queryset.filter(created__month='3', created__year=datetime.datetime.now().year)
        if self.value() == '4':
            return queryset.filter(created__month='4', created__year=datetime.datetime.now().year)
        if self.value() == '5':
            return queryset.filter(created__month='5', created__year=datetime.datetime.now().year)
        if self.value() == '6':
            return queryset.filter(created__month='6', created__year=datetime.datetime.now().year)
        if self.value() == '7':
            return queryset.filter(created__month='7', created__year=datetime.datetime.now().year)
        if self.value() == '8':
            return queryset.filter(created__month='8', created__year=datetime.datetime.now().year)
        if self.value() == '9':
            return queryset.filter(created__month='9', created__year=datetime.datetime.now().year)
        if self.value() == '10':
            return queryset.filter(created__month='10', created__year=datetime.datetime.now().year)
        if self.value() == '11':
            return queryset.filter(created__month='11', created__year=datetime.datetime.now().year)
        if self.value() == '12':
            return queryset.filter(created__month='12', created__year=datetime.datetime.now().year)




@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'city', 'from_address', 'to_address', 'status', 'created', 'selected_driver']
    list_filter = ['status', 'city', OrderMonthFilter, 'created']
    fieldsets = (
        (None,{'fields': ('phone_number', 'city', 'from_address', 'to_address', 'status', 'created', 'selected_driver')}),
    )
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

# class OverpaymentFilter(admin.SimpleListFilter)
#     title = 'Фильтр по городам'
#     parameter_name = 'date'
#
#     def lookups(self, request, model_admin):
#         return (
#             ('день', 'День'),
#             ('неделя', 'Неделя'),
#             ('месяц', 'Месяц'),
#             ('год', 'Год'),
#
#         )
#
#     def queryset(self, request, queryset):
#         if self.value() == 'день':
#             return queryset.filter(created__gte=datetime.datetime.today() - datetime.timedelta(days=1))
#         if self.value() == 'неделя':
#             return queryset.filter(created__gte=datetime.datetime.today() - datetime.timedelta(days=7))
#         if self.value() == 'месяц':
#             return queryset.filter(created__gte=datetime.datetime.today() - datetime.timedelta(days=30))
#         if self.value() == 'год':
#             return queryset.filter(created__gte=datetime.datetime.today() - datetime.timedelta(days=365))


@admin.register(Overpayment)
class OverpaymentAdmin(admin.ModelAdmin):
    list_display = ['driver', 'amount']
    list_filter = ['driver__city', 'order__created']
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.unregister(Site)