from django.shortcuts import render, redirect
from django.views import generic
from .models import City, Order, OfferOrder, Review
from user_auth.models import User
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
        # user_ip = get_client_ip(request)
        cities = City.objects.all()
        # yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        # my_orders = Order.objects.filter(user_ip=user_ip, created__gte=yesterday, review=None).exclude(status='canceled')

        count_online_drivers = 0
        for user in User.objects.all():
            if user.online and user.is_free:
                count_online_drivers +=1
        self.extra_context = {
            'cities': cities,
            # 'my_orders': my_orders,
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

            Order.objects.create(user_ip=user_ip, from_address=from_address, to_address=to_address, phone_number=phone_number, city=city)
        elif 'choose' in request.POST:
            offer = OfferOrder.objects.get(id=int(request.POST['offer_id']))
            offer.is_selected = True
            driver = offer.driver_offer
            driver.balance -= offer.order.city.overpayment
            driver.is_free = False
            driver.save()
            order = offer.order
            order.selected_driver = driver
            order.status = 'started'
            order.save()
            offer.save()
        elif 'cancel' in request.POST:
            order = Order.objects.get(id=int(request.POST['cancel']))
            order.status = 'canceled'
            driver = order.selected_driver
            driver.is_free = True
            driver.save()
            order.save()
            order.delete()
        elif 'review' in request.POST:
            order = Order.objects.get(id=int(request.POST['order_id']))
            print(order)
            rating = request.POST['rating']
            comment = request.POST['comment']
            Review.objects.create(order=order, comment=comment, rating=rating)
        return redirect('home_view')


def getMyOrders(request):
    user_ip = get_client_ip(request)

    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    my_orders = Order.objects.filter(user_ip=user_ip, created__gte=yesterday, review=None).exclude(status='canceled')
    return render(request, 'mainapp/ajax_my_orders.html', {'my_orders': my_orders})