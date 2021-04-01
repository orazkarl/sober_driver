from django.shortcuts import render, redirect, reverse
from django.http import HttpResponseRedirect
from django.contrib import messages

from django.views import generic
from .models import City, Order, OfferOrder, Review, Overpayment
from user_auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone
import datetime


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class HomeView(generic.TemplateView):
    template_name = 'mainapp/index.html'

    def get(self, request, *args, **kwargs):
        all_orders = Order.objects.filter(status='started',
                                          started_date__lte=datetime.datetime.now() - datetime.timedelta(
                                              minutes=10)).exclude(selected_driver=None)
        for order in all_orders:
            order.status = 'finished'
            order.save()
            driver = order.selected_driver
            driver.is_free = True
            driver.save()
        all_orders = Order.objects.filter(status='request',
                                          created__lte=datetime.datetime.now() - datetime.timedelta(minutes=30))
        for order in all_orders:
            order.status = 'canceled'
            order.save()
        cities = City.objects.all()
        count_online_drivers = 0
        user_ip = get_client_ip(request)
        orders = Order.objects.filter(user_ip=user_ip)
        bookmark = False
        if orders.count() >= 1 and orders.count() < 2:
            if orders.first().status == 'request':
                bookmark = True
        active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
        user_id_list = []
        for session in active_sessions:
            data = session.get_decoded()
            user_id_list.append(data.get('_auth_user_id', None))
        # Query all logged in users based on id list
        city = 'Алматы'
        if orders.exists():
            city = orders.first().city
        count_online_drivers = User.objects.filter(id__in=user_id_list, is_free=True, city__name=city).count()
        list(messages.get_messages(request))
        self.extra_context = {
            'cities': cities,
            # 'my_orders': my_orders,
            'count_online_drivers': count_online_drivers,
            'bookmark': bookmark,
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if 'order' in request.POST:
            user_ip = get_client_ip(request)
            from_address = request.POST['from_address']
            to_address = request.POST['to_address']
            phone_number = request.POST['phone_number']
            city = City.objects.get(name=request.POST['city'])

            Order.objects.create(user_ip=user_ip, from_address=from_address, to_address=to_address,
                                 phone_number=phone_number, city=city)
            for message in messages.get_messages(request):
                print(message)
            messages.add_message(self.request, messages.SUCCESS, 'top_scrool')

            # return render(request, template_name='mainapp/index.html', )
        elif 'choose' in request.POST:
            offer = OfferOrder.objects.get(id=int(request.POST['offer_id']))
            driver = offer.driver_offer
            if driver.is_free == False:
                return redirect('home_view')
            offer.is_selected = True
            # if driver.balance < offer.order.city.overpayment:
            #     return redirect('home_view')
            driver.balance -= offer.order.city.overpayment
            driver.is_free = False
            driver.save()
            Overpayment.objects.create(driver=driver, amount=int(offer.order.city.overpayment), order=offer.order)
            order = offer.order
            order.selected_driver = driver
            order.status = 'started'
            order.started_date = datetime.datetime.now()
            order.is_view = True
            order.save()
            offer.save()
        elif 'cancel' in request.POST:
            order = Order.objects.get(id=int(request.POST['cancel']))
            order.status = 'canceled'
            order.save()
        elif 'rating' in request.POST:
            order = Order.objects.get(id=int(request.POST['order_id']))
            rating = request.POST['rating']
            Review.objects.create(order=order, rating=rating)
        elif 'not_review' in request.POST:
            order = Order.objects.get(id=int(request.POST['order_id']))
            Review.objects.create(order=order, rating=1)
            order.no_rating = True
            order.save()
        return redirect('home_view')


def getMyOrders(request):
    user_ip = get_client_ip(request)
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    my_orders = Order.objects.filter(user_ip=user_ip, created__gte=yesterday).exclude(status='canceled').exclude(
        status='finished')
    for order in my_orders.filter(status='started').exclude(selected_driver=None):
        for offer in order.offers.all():
            if order.minutes and order.seconds:
                duration = order.minutes * 60 + order.seconds
            else:
                if offer.driver_offer == order.selected_driver:
                    duration = offer.time * 60
            duration -= 1
            minutes = int(duration / 60)
            seconds = int(duration % 60)
            order.minutes = minutes
            order.seconds = seconds
            order.save()

    return render(request, 'mainapp/ajax_my_orders.html', {'my_orders': my_orders})
