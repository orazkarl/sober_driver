from django.shortcuts import render, redirect
from django.views import generic
from .models import City, Order, OfferOrder


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
        user_ip = get_client_ip(request)
        cities = City.objects.all()
        my_orders = Order.objects.filter(user_ip=user_ip, status='request')
        self.extra_context = {
            'cities': cities,
            'my_orders': my_orders,
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user_ip = get_client_ip(request)
        from_address = request.POST['from_address']
        to_address = request.POST['to_address']
        phone_number = request.POST['phone_number']
        city = City.objects.get(name=request.POST['city'])

        Order.objects.create(user_ip=user_ip, from_address=from_address, to_address=to_address, phone_number=phone_number, city=city)
        return redirect('home_view')
