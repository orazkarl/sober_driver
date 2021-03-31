from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.cache import cache
import datetime
from sober_driver import settings
from mainapp.models import City
import numpy as np


class UserManager(BaseUserManager):
    def create_superuser(self, phone_number, country_code, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("User must have an phone_number")
        if not password:
            raise ValueError("User must have a password")
        if not country_code:
            raise ValueError("User must have a full country_code")

        user = self.model(phone_number=phone_number)
        user.country_code = country_code
        user.set_password(password)
        user.is_active = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    KNOWLEDGE_CITY_CHOICES = [
        ['5', 'отлично'],
        ['4', 'хорошо'],
        ['3', 'нормально'],
        ['2', 'немножко'],
        ['1', 'незнаю'],
    ]
    username = None
    driving_experience = models.PositiveIntegerField('Стаж вождение', default=0)
    avatar = models.FileField(upload_to='avatars/', blank=True)
    iin = models.CharField('ИИН', max_length=12, blank=True)
    driver_license_number = models.CharField('Номер водительского удостоверение', max_length=20, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='users', verbose_name='Город', blank=True,
                             null=True)

    trip_from_price = models.PositiveIntegerField(default=0)
    trip_hour_price = models.PositiveIntegerField(default=0)
    average_arrival = models.PositiveIntegerField(default=0)
    knowledgecity = models.CharField(max_length=10, null=True, blank=True, choices=KNOWLEDGE_CITY_CHOICES)
    bio = models.CharField('Информация о водителя', max_length=18, null=True, blank=True)
    phone_number = models.BigIntegerField('Телефон', unique=True)
    country_code = models.IntegerField()
    phone_number_verified = models.BooleanField(default=False)
    balance = models.IntegerField('Баланс', default=0)
    active_subscription = models.BooleanField('Есть подписка?', default=False)
    subscription_day = models.DateTimeField('Дата окончание подписки', null=True, blank=True)
    is_free = models.BooleanField(default=True)
    is_block = models.BooleanField('Заблокированный', default=False)
    front_passport = models.FileField('Уд. лич. (Лицевая сторона)', blank=True, null=True, upload_to='passports/')
    back_passport = models.FileField('Уд. лич. (Обратная сторона)', blank=True, null=True)
    together_passport = models.FileField('Фото с уд. личности', blank=True, null=True)
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['country_code']

    objects = UserManager()

    def __str__(self):
        return self.first_name

    def last_seen(self):
        return cache.get('seen_%s' % self.first_name)

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

    def average_rating(self):
        all_ratings = map(lambda x: x.review.rating,
                          self.orders.filter(status='finished', no_rating=False).exclude(review=None))
        avg_rating = np.mean(list(all_ratings))
        if str(avg_rating) == 'nan':
            return 0

        return round(avg_rating)
