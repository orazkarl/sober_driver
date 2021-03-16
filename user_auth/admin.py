from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


# admin.site.register(User)

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ['first_name', 'last_name', 'phone_number', 'balance', 'date_joined', 'last_login']
    # list_filter = ['is_buyer', 'is_clone']
    # search_fields = ['username']
    # paginator = 30
    ordering = ['first_name']
    fieldsets = (
        (None,
         {'fields': ('password', 'country_code','phone_number')}),
        (('Личная информация'),
         {'fields': (
             'first_name', 'last_name', 'driving_experience', 'city', 'iin', 'driver_license_number', 'avatar', 'active_subscription', 'subscription_day', 'balance')}),
        (('Права доступа'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_free'),
        }),
        ('Дата и время', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'country_code', 'phone_number', 'first_name', 'last_name', 'city', 'driving_experience', 'iin', 'driver_license_number','avatar' ,'password1',
                'password2', 'is_active',
                'is_staff', 'is_superuser'),
        }),
    )


from django.contrib.auth.models import Group
admin.site.unregister(Group)