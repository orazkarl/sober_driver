from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from user_auth.models import User
from mainapp.models import City, Order, OfferOrder
from .models import TechInstructions
from datetime import timedelta, datetime
from django.http import JsonResponse
from django.db import models
from django.contrib.auth.decorators import user_passes_test

from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


def pass_anketa(user):
    if user.trip_from_price \
            and user.trip_hour_price \
            and user.average_arrival \
            and user.knowledgecity \
            and user.bio \
            and user.front_passport \
            and user.back_passport \
            and user.together_passport \
            and user.driving_experience \
            and user.avatar \
            and user.iin \
            and user.driver_license_number \
            and user.driving_experience:
        return True
    return False


def compressImage(uploadedImage):
    imageTemproary = Image.open(uploadedImage)
    outputIoStream = BytesIO()
    # imageTemproaryResized = imageTemproary.resize((1020, 573))
    imageTemproary.save(outputIoStream, format='JPEG', quality=60)
    # outputIoStream.seek(0)
    uploadedImage = InMemoryUploadedFile(outputIoStream, 'ImageField', "%s.jpg" % uploadedImage.name.split('.')[0],
                                         'image/jpeg', sys.getsizeof(outputIoStream), None)

    return uploadedImage


@method_decorator([login_required, user_passes_test(pass_anketa, login_url='/anketa/')], name='dispatch')
class ProfileView(generic.TemplateView):
    template_name = 'profileapp/profile.html'

    def get(self, request, *args, **kwargs):
        d0 = datetime.now().date()
        if request.user.subscription_day:
            d1 = request.user.subscription_day.date()
            subscription_days = (d1 - d0).days
        else:
            subscription_days = 0
        orders = Order.objects.filter(selected_driver=request.user, status='finished')
        count_orders_day = orders.filter(created__gte=datetime.today() - timedelta(days=1)).count()
        count_orders_week = orders.filter(created__gte=datetime.today() - timedelta(days=7)).count()
        count_orders_month = orders.filter(selected_driver=request.user, status='finished',
                                           created__gte=datetime.today() - timedelta(days=30)).count()
        count_orders_all = orders.count()
        offer_orders = OfferOrder.objects.filter(driver_offer=request.user, order__status='finished')
        amount_income_day = \
            offer_orders.filter(order__created__gte=datetime.today() - timedelta(days=1)).aggregate(
                models.Sum('price'))[
                'price__sum']
        amount_income_week = \
            offer_orders.filter(order__created__gte=datetime.today() - timedelta(days=7)).aggregate(
                models.Sum('price'))[
                'price__sum']
        amount_income_month = \
            offer_orders.filter(order__created__gte=datetime.today() - timedelta(days=30)).aggregate(
                models.Sum('price'))[
                'price__sum']
        amount_income_all = offer_orders.aggregate(models.Sum('price'))['price__sum']

        self.extra_context = {
            'subscription_days': subscription_days,
            'count_orders_day': count_orders_day,
            'count_orders_week': count_orders_week,
            'count_orders_month': count_orders_month,
            'count_orders_all': count_orders_all,
            'amount_income_day': amount_income_day,
            'amount_income_week': amount_income_week,
            'amount_income_month': amount_income_month,
            'amount_income_all': amount_income_all,

        }
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if 'subscription' in request.POST:
            user = request.user
            if user.balance >= 500:
                user.balance -= 500
                user.active_subscription = True
                if user.subscription_day:
                    user.subscription_day = user.subscription_day + timedelta(days=7)
                else:
                    user.subscription_day = datetime.now() + timedelta(days=7)
                user.save()
            else:
                messages.add_message(request, messages.ERROR, 'Недостаточно денег на балансе')
        return redirect('profile_view')


@method_decorator([login_required, user_passes_test(pass_anketa, login_url='/anketa/')], name='dispatch')
class OrdersView(generic.ListView):
    template_name = 'profileapp/orders.html'
    model = Order


def getOrders(request):
    user = request.user

    if user.is_free:
        orders = Order.objects.filter(city=user.city, selected_driver=None).exclude(status='finished').exclude(
            status='canceled').exclude(status='notselected')
    else:
        orders = Order.objects.filter(selected_driver=user).exclude(status='finished').exclude(
            status='canceled').exclude(status='notselected')
    return render(request, 'profileapp/ajax_orders.html', {'orders': orders})


@method_decorator([login_required, user_passes_test(pass_anketa, login_url='/anketa/')], name='dispatch')
class OrderDetailView(generic.DetailView):
    model = Order
    template_name = 'profileapp/order_detail.html'

    def get(self, request, *args, **kwargs):
        order = Order.objects.get(id=self.kwargs['pk'])
        if order.status == 'request':
            offer = ''
            if order.offers.filter(driver_offer=request.user).exists():
                offer = order.offers.filter(driver_offer=request.user)[0]
            self.extra_context = {
                'offer': offer,
            }
            return super().get(request, *args, **kwargs)
        else:
            return redirect('orders_view')

    def post(self, request, *args, **kwargs):
        user = request.user
        if user.balance < user.city.overpayment:
            return redirect('orders_view')
        order = Order.objects.get(id=self.kwargs['pk'])
        price = 0
        if 'price' in request.POST:
            price = request.POST['price']
        time = request.POST['time']
        # comment = request.POST['comment']
        OfferOrder.objects.create(order=order, driver_offer=request.user, time=time, price=price)
        return super().get(request, *args, **kwargs)


@method_decorator([login_required, user_passes_test(pass_anketa, login_url='/anketa/')], name='dispatch')
class InstructionView(generic.TemplateView):
    template_name = 'profileapp/instruction.html'

    def get(self, request, *args, **kwargs):
        instruction = TechInstructions.objects.all().first()
        self.extra_context = {
            'instruction': instruction,
        }
        return super().get(request, *args, **kwargs)


@method_decorator([login_required, user_passes_test(pass_anketa, login_url='/anketa/')], name='dispatch')
class SettingsView(generic.TemplateView):
    template_name = 'profileapp/settings.html'

    def post(self, request, *args, **kwargs):
        user = request.user

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
                user.avatar = compressImage(avatar)
                user.save()
                messages.add_message(request, messages.SUCCESS, 'Фото изменено')
        elif 'change_driver_license_number' in request.POST:
            driver_license_number = request.POST['driver_license_number']
            user.driver_license_number = driver_license_number
            user.save()
        elif 'change_bio' in request.POST:
            driving_experience = request.POST['driving_experience']
            trip_from_price = request.POST['trip_from_price']
            trip_hour_price = request.POST['trip_hour_price']
            average_arrival = request.POST['average_arrival']
            knowledgecity = request.POST['knowledgecity']
            disctrict = request.POST['disctrict']
            bio = request.POST['bio']
            user.driving_experience = driving_experience
            user.trip_from_price = trip_from_price
            user.trip_hour_price = trip_hour_price
            user.average_arrival = average_arrival
            user.knowledgecity = knowledgecity
            user.disctrict = disctrict
            user.bio = bio
            user.save()
        return redirect('settings_view')


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class AnketaView(generic.TemplateView):
    template_name = 'profileapp/anketa.html'

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.trip_from_price and user.trip_hour_price and user.average_arrival and user.knowledgecity and user.bio and user.front_passport and user.back_passport and user.together_passport and user.driving_experience and user.avatar and user.iin and user.driver_license_number and user.driving_experience:
            return redirect('instruction_view')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user = request.user
        if 'change_bio' in request.POST:
            driving_experience = request.POST['driving_experience']
            trip_from_price = request.POST['trip_from_price']
            trip_hour_price = request.POST['trip_hour_price']
            average_arrival = request.POST['average_arrival']
            knowledgecity = request.POST['knowledgecity']
            disctrict = request.POST['disctrict']
            bio = request.POST['bio']
            user.driving_experience = driving_experience
            user.trip_from_price = trip_from_price
            user.trip_hour_price = trip_hour_price
            user.average_arrival = average_arrival
            user.knowledgecity = knowledgecity
            user.disctrict = disctrict
            user.bio = bio
            user.save()
        elif 'add_front_passport' in request.POST:
            if request.FILES:
                front_passport = request.FILES['front_passport']
                user.front_passport = front_passport
                user.save()
        elif 'add_back_passport' in request.POST:
            if request.FILES:
                back_passport = request.FILES['back_passport']
                user.back_passport = back_passport
                user.save()
        elif 'add_together_passport' in request.POST:
            if request.FILES:
                together_passport = request.FILES['together_passport']
                user.together_passport = together_passport
                user.save()
        elif 'add_avatar' in request.POST:
            if request.FILES:
                avatar = request.FILES['avatar']
                user.avatar = compressImage(avatar)
                user.save()
        elif 'add_driver_license_number' in request.POST:
            driver_license_number = request.POST['driver_license_number']
            user.driver_license_number = driver_license_number
            user.save()
        elif 'add_iin' in request.POST:
            iin = request.POST['iin']
            user.iin = iin
            user.save()
        return redirect('anketa_view')
