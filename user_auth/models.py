from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.cache import cache
import datetime
from sober_driver import settings
from mainapp.models import City


class User(AbstractUser):
    username = None
    driving_experience = models.PositiveIntegerField('Стаж вождение', default=0)
    avatar = models.FileField(upload_to='avatars/', blank=True)
    iin = models.CharField('ИИН', max_length=12, blank=True)
    driver_license_number = models.CharField('Номер водительского удостоверение', max_length=20, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='users', verbose_name='Город', blank=True,
                             null=True)
    phone_number = models.BigIntegerField('Телефон', unique=True)
    country_code = models.IntegerField()
    phone_number_verified = models.BooleanField(default=False)
    balance = models.IntegerField('Баланс', default=0)
    active_subscription = models.BooleanField('Есть подписка?', default=False)
    subscription_day = models.DateTimeField('Дата окончание подписки', null=True, blank=True)
    is_free = models.BooleanField(default=True)
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['country_code']

    def __str__(self):
        return self.first_name

    def last_seen(self):
        return cache.get('seen_%s' % self.user.username)

    def online(self):
        if self.last_seen():
            now = datetime.datetime.now()
            if now > self.last_seen() + datetime.timedelta(
                    seconds=settings.USER_ONLINE_TIMEOUT):
                return False
            else:
                return True
        else:
            return False