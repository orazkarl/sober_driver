from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.views import generic
from .models import City, Order, OfferOrder, Review, Overpayment
from user_auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone
import datetime
from .tasks import update_order_status_finished, update_order_status_notselected
from background_task.models import Task


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
        count_online_drivers = 0
        city = 'Алматы'
        active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
        user_id_list = []
        for session in active_sessions:
            data = session.get_decoded()
            user_id_list.append(data.get('_auth_user_id', None))
        count_online_drivers = User.objects.filter(id__in=user_id_list, is_free=True, city__name=city).count()
        list(messages.get_messages(request))
        cities = City.objects.all()
        self.extra_context = {
            'cities': cities,
            'count_online_drivers': count_online_drivers,
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if 'order' in request.POST:
            user_ip = get_client_ip(request)
            from_address = request.POST['from_address']
            to_address = request.POST['to_address']
            phone_number = request.POST['phone_number']
            city = City.objects.get(name=request.POST['city'])

            order = Order.objects.create(user_ip=user_ip, from_address=from_address, to_address=to_address,
                                         phone_number=phone_number, city=city)
            update_order_status_notselected(order_id=order.id, verbose_name='task' + str(order.id))

            for message in messages.get_messages(request):
                print(message)
            messages.add_message(self.request, messages.SUCCESS, 'top_scrool')
        elif 'choose' in request.POST:
            print(111)
            offer = OfferOrder.objects.get(id=int(request.POST['offer_id']))
            driver = offer.driver_offer
            if driver.is_free == False:
                return redirect('home_view')
            offer.is_selected = True
            if driver.restriction < 1:
                driver.balance -= offer.order.city.overpayment
                Overpayment.objects.create(driver=driver, amount=int(offer.order.city.overpayment), order=offer.order)
            else:
                driver.restriction -= 1
            driver.is_free = False
            driver.save()
            order = offer.order
            order.selected_driver = driver
            order.status = 'started'
            order.started_date = datetime.datetime.now()
            order.is_view = True
            order.save()
            offer.save()
            update_order_status_finished(order_id=order.id)
            task = Task.objects.get(verbose_name='task' + str(order.id))
            task.delete()
        elif 'cancel' in request.POST:
            order = Order.objects.get(id=int(request.POST['cancel']))
            order.status = 'canceled'
            order.save()
        elif 'rating' in request.POST:
            order = Order.objects.get(id=int(request.POST['order_id']))
            rating = request.POST['rating']
            Review.objects.create(order=order, rating=rating)
        return redirect('home_view')


def getMyOrders(request):
    user_ip = get_client_ip(request)
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    my_orders = Order.objects.filter(user_ip=user_ip, created__gte=yesterday).exclude(status='canceled').exclude(
        status='finished').exclude(status='notselected')
    return render(request, 'mainapp/ajax_my_orders.html', {'my_orders': my_orders})
