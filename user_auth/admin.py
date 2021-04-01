from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User

import datetime


class DriverFilter(admin.SimpleListFilter):
    title = 'Водители'
    parameter_name = 'driver'

    def lookups(self, request, model_admin):
        return (
            ('active', 'Активные водители'),
            ('new', 'Новые водители'),


        )

    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(orders__status='finished', orders__created__gte=datetime.datetime.today() - datetime.timedelta(days=7)).distinct()
        if self.value() == 'new':
            return queryset.filter(date_joined__gte=datetime.datetime.today() - datetime.timedelta(days=7))

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ['phone_number','first_name', 'last_name', 'balance', 'count_orders_day', 'count_orders_week', 'count_orders_month', 'count_orders', 'average_rating']
    list_filter = ['active_subscription', DriverFilter]
    # search_fields = ['username']
    # paginator = 30
    ordering = ['first_name']

    # readonly_fields = ['password', 'country_code', 'phone_number', 'first_name', 'last_name', 'driver_license_number',
    #                    'avatar', 'active_subscription', 'subscription_day', 'last_login', 'date_joined']
    fieldsets = (
        (None,
         {'fields': ('password', 'country_code', 'phone_number')}),
        (('Личная информация'),
         {'fields': (
             'first_name', 'last_name', 'driving_experience', 'city', 'iin', 'driver_license_number', 'avatar', 'front_passport', 'back_passport', 'together_passport',
             'active_subscription', 'subscription_day', 'balance', 'bio')}),
        (('Права доступа'), {
            'fields': ('is_block', 'is_free'),
        }),
        ('Дата и время', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'country_code', 'phone_number', 'first_name', 'last_name', 'city', 'driving_experience', 'iin',
                'driver_license_number', 'avatar', 'password1',
                'password2', 'is_active',
                'is_staff', 'is_superuser'),
        }),
    )

    def has_add_permission(self, request):
        return False

    def count_orders_day(self,obj=None):
        return f"{obj.orders.filter(status='finished', created__gte=datetime.datetime.today() - datetime.timedelta(days=1)).count()}"
    count_orders_day.short_description = 'Кол. заказов за день'
    def count_orders_week(self,obj=None):
        return f"{obj.orders.filter(status='finished', created__gte=datetime.datetime.today() - datetime.timedelta(days=7)).count()}"
    count_orders_week.short_description = 'Кол. заказов за неделю'
    def count_orders_month(self,obj=None):
        return f"{obj.orders.filter(status='finished', created__gte=datetime.datetime.today() - datetime.timedelta(days=30)).count()}"
    count_orders_month.short_description = 'Кол. заказов за месяц'
    def count_orders(self,obj=None):
        return f"{obj.orders.filter(status='finished').count()}"
    count_orders.short_description = 'Общ. кол. заказов'


from django.contrib.auth.models import Group

admin.site.unregister(Group)
