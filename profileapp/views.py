from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from user_auth.models import User
from mainapp.models import City, Order, OfferOrder
from datetime import timedelta, datetime
from django.http import JsonResponse


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class ProfileView(generic.TemplateView):
    template_name = 'profileapp/profile.html'

    def get(self, request, *args, **kwargs):
        date_format = "%m/%d/%Y"
        d0 = datetime.now().date()
        d1 = request.user.subscription_day.date()
        subscription_days = (d1 - d0).days
        self.extra_context = {
            'subscription_days': subscription_days,
        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if 'subscription' in request.POST:
            user = request.user
            if user.balance >= 500:
                user.balance -= 500
                user.active_subscription = True
                if user.subscription_day:
                    user.subscription_day = user.subscription_day + timedelta(days=30)
                else:
                    user.subscription_day = datetime.now() + timedelta(days=30)
                user.save()
            else:
                messages.add_message(request, messages.ERROR, 'Недостаточно денег на балансе')
        return redirect('prodile_view')


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class OrdersView(generic.ListView):
    template_name = 'profileapp/orders.html'
    model = Order

    def get(self, request, *args, **kwargs):
        user = request.user
        orders = Order.objects.filter(city=user.city, status='request')
        self.extra_context = {
            'orders': orders,
        }

        return super().get(request, *args, **kwargs)

    # def post(self, request, *args, **kwargs):
    #     order = Order.objects.get(id=int(request.POST['order_id']))
    #     OfferOrder.objects.create()
    #     return redirect('orders_view')


# def getOrders(request):
#     queryset = Order.objects.filter(city=request.user.city, status='request')
#     return JsonResponse({"orders": list(queryset.values())})

@method_decorator(login_required(login_url='/login/'), name='dispatch')
class OrderDetailView(generic.DetailView):
    model = Order
    template_name = 'profileapp/order_detail.html'

    def post(self, request, *args, **kwargs):
        order = Order.objects.get(id=self.kwargs['pk'])
        price = request.POST['price']
        time = request.POST['time']
        comment = request.POST['comment']
        OfferOrder.objects.create(order=order, driver_offer=request.user, comment=comment, time=time)
        return redirect('orders_view')


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class InstructionView(generic.TemplateView):
    template_name = 'profileapp/instruction.html'


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class SettingsView(generic.TemplateView):
    template_name = 'profileapp/settings.html'

    def post(self, request, *args, **kwargs):
        user = request.user
        print(1)
        if 'change_phone_number' in request.POST:
            old_country_code = int(request.POST['old_country_code'])
            old_phone_number = int(request.POST['old_phone_number'])
            new_country_code = int(request.POST['new_country_code'])
            new_phone_number = int(request.POST['new_phone_number'])
            if old_country_code != (user.country_code):
                messages.add_message(request, messages.ERROR, 'Неправильный код страны старого  номера')

                return redirect('settings_view')
            elif old_phone_number != user.phone_number:
                messages.add_message(request, messages.ERROR, 'Неправильный старой номер телефона')
                return redirect('settings_view')
            elif User.objects.filter(phone_number=new_phone_number, country_code=new_country_code).exists():

                messages.add_message(request, messages.ERROR, 'Этот номер уже используется')
                return redirect('settings_view')
            user.country_code = new_country_code
            user.phone_number = new_phone_number
            user.save()
            messages.add_message(request, messages.SUCCESS, 'Номер телефона успешно изменен')
        elif 'change_avatar' in request.POST:
            if request.FILES:
                avatar = request.FILES['avatar']
                user.avatar = avatar
                user.save()
                messages.add_message(request, messages.SUCCESS, 'Фото изменено')
        return redirect('settings_view')
