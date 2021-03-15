from django.db import models
from django.conf import settings


class City(models.Model):
    name = models.CharField('Название', max_length=50)
    overpayment = models.PositiveIntegerField('Цена за каждый заказ', default=0)
    subscription_price = models.PositiveIntegerField('Цена подписки', default=0)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Городы'


class Order(models.Model):
    STATUSES = (
        ('request', 'Запрос'),
        ('started', 'Началось'),
        # ('in_progress', 'В процессе'),
        ('finished', 'Завершенный'),
        ('canceled', 'Отменен')
    )

    selected_driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True,
                                        related_name='orders', verbose_name='Водитель')
    user_ip = models.CharField('IP адрес пользователя', max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='orders', verbose_name='Город')
    from_address = models.CharField('Откуда', max_length=255)
    to_address = models.CharField('Куда', max_length=255)
    phone_number = models.CharField('Номер телефона', max_length=15)
    status = models.CharField('Статус', max_length=50, choices=STATUSES, default='request')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return self.phone_number


class OfferOrder(models.Model):
    order = models.ForeignKey(Order, related_name='offers', on_delete=models.CASCADE, verbose_name='Заказ')
    driver_offer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='offers',
                                     verbose_name='Предложения водителя')
    price = models.IntegerField('Цена', default=0)
    comment = models.TextField('Комментария', max_length=500)
    time = models.IntegerField('Время (минутах)')
    is_selected = models.BooleanField('Выбран', default=False)

    def __str__(self):
        return str(self.driver_offer)


class Review(models.Model):
    RATING_CHOICES = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
    )
    order = models.OneToOneField(Order, on_delete=models.CASCADE, verbose_name='Заказ', related_name='review')
    comment = models.TextField('Комментарий', max_length=250, null=True, blank=True)
    rating = models.PositiveIntegerField('Рейтинг', choices=RATING_CHOICES)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.order)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
