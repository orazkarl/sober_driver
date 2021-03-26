from django.shortcuts import render, redirect
from django.views import generic
from .models import City, Order, OfferOrder, Review
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
        all_orders = Order.objects.filter(status='started', created__lte=datetime.datetime.now() - datetime.timedelta(minutes=10))
        for order in all_orders:
            order.status = 'finished'
            order.save()
            driver = order.selected_driver
            driver.is_free = True
            driver.save()
        all_orders = Order.objects.filter(status='request', created__lte=datetime.datetime.now() - datetime.timedelta(minutes=30))
        for order in all_orders:
            order.status = 'canceled'
            order.save()
        cities = City.objects.all()
        count_online_drivers = 0
        user_ip = get_client_ip(request)
        orders = Order.objects.filter(user_ip=user_ip)
        bookmark = False
        if orders.count() >= 1 and orders.count() < 2:
            bookmark = True
        active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
        user_id_list = []
        for session in active_sessions:
            data = session.get_decoded()
            print(data)
            user_id_list.append(data.get('_auth_user_id', None))
        # Query all logged in users based on id list
        count_online_drivers = User.objects.filter(id__in=user_id_list, is_free=True).count()

        # for user in User.objects.all():
        #     if user.online() and user.is_free:
        #         count_online_drivers +=1

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
        elif 'choose' in request.POST:
            offer = OfferOrder.objects.get(id=int(request.POST['offer_id']))
            driver = offer.driver_offer
            if driver.is_free == False:
                return redirect('home_view')
            offer.is_selected = True
            if driver.balance < offer.order.city.overpayment:
                return redirect('home_view')
            driver.balance -= offer.order.city.overpayment
            driver.is_free = False
            driver.save()
            order = offer.order
            order.selected_driver = driver
            order.status = 'started'
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
    return render(request, 'mainapp/ajax_my_orders.html', {'my_orders': my_orders})
