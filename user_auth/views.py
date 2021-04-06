from django.shortcuts import render, HttpResponse, redirect
from django.views.generic import TemplateView, FormView
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
import json
from .forms import RegisterForm, LoginForm, PhoneVerificationForm, RestorePasswordForm, RestorePasswordConfirmForm, InsertNewPasswordForm
from .authy_api import send_verfication_code, verify_sent_code
from .models import User, PrivacyPolicy


class RegisterView(SuccessMessageMixin, FormView):
    template_name = 'user_auth/register.html'
    form_class = RegisterForm
    success_message = "Одноразовый пароль, отправленный на ваш зарегистрированный номер мобильного телефона. \
                         Код подтверждения действителен в течение 10 минут."

    def form_valid(self, form):
        user = form.save()
        phone_number = self.request.POST['phone_number']
        password = self.request.POST['password1']
        user = authenticate(username=phone_number, password=password)

        try:
            response = send_verfication_code(user)
        except Exception as e:
            messages.add_message(self.request, messages.ERROR,
                                 'код подтверждения не отправлен. \n'
                                 'Пожалуйста, перерегистрируйтесь.')
            return redirect('/register')
        data = json.loads(response.text)
        if data['success'] == False:
            messages.add_message(self.request, messages.ERROR,
                                 data['message'])
            return redirect('/register')

        else:
            kwargs = {'user': user}

            self.request.method = 'GET'
            return PhoneVerificationView(self.request, **kwargs)


def PhoneVerificationView(request, **kwargs):
    template_name = 'user_auth/phone_confirm.html'
    if request.method == "POST":
        phone_number = request.POST['phone_number']
        user = User.objects.get(phone_number=phone_number)
        form = PhoneVerificationForm(request.POST)
        if form.is_valid():
            verification_code = request.POST['one_time_password']
            response = verify_sent_code(verification_code, user)
            data = json.loads(response.text)

            if data['success'] == True:
                login(request, user)
                if user.phone_number_verified is False:
                    user.phone_number_verified = True
                    user.save()
                return redirect('prodile_view')
            else:
                messages.add_message(request, messages.ERROR,
                                     data['message'])
                return render(request, template_name, {'user': user})
        else:
            context = {
                'user': user,
                'form': form,
            }
            return render(request, template_name, context)

    elif request.method == "GET":
        if 'user' in kwargs:
            user = kwargs['user']
            return render(request, template_name, {'user': user})
        else:
            return HttpResponse("Not Allowed")

        # try:
        #     user = kwargs['user']
        #     return render(request, template_name, {'user': user})
        # except:
        #     return HttpResponse("Not Allowed")


class LoginView(FormView):
    template_name = 'user_auth/login.html'
    form_class = LoginForm
    success_url = 'profile_view'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:

            messages.add_message(self.request, messages.INFO, "Пользователь уже вошел в систему")
            return redirect('profile_view')
        else:
            return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.login(self.request)
        login(self.request, user)
        return redirect('profile_view')


class RestorePasswordView(FormView):
    template_name = 'user_auth/restore_password.html'
    form_class = RestorePasswordForm

    def form_valid(self, form):
        phone_number = self.request.POST['phone_number']

        user = User.objects.get(phone_number=phone_number)
        try:
            response = send_verfication_code(user)
        except Exception as e:
            messages.add_message(self.request, messages.ERROR,
                                 'Пользователь с таким номером не существует')
            return redirect('restore_password')
        data = json.loads(response.text)
        if data['success'] == False:
            messages.add_message(self.request, messages.ERROR,
                                 data['message'])
            return redirect('restore_password')

        else:
            kwargs = {'user': user}
            self.request.method = 'GET'
            return RestorePasswordConfirmView(self.request, **kwargs)


def RestorePasswordConfirmView(request, **kwargs):
    template_name = 'user_auth/restore_password_confirm.html'
    if request.method == "POST":
        phone_number = request.POST['phone_number']
        user = User.objects.get(phone_number=phone_number)
        form = RestorePasswordConfirmForm(request.POST)
        if form.is_valid():
            verification_code = request.POST['one_time_password']
            response = verify_sent_code(verification_code, user)
            data = json.loads(response.text)

            if data['success'] == True:
                return render(request, 'user_auth/insert_password.html', {'user': user})
            else:
                messages.add_message(request, messages.ERROR,
                                     data['message'])
                return render(request, template_name, {'user': user})
        else:
            context = {
                'user': user,
                'form': form,
            }
            return render(request, template_name, context)

    elif request.method == "GET":
        if 'user' in kwargs:
            user = kwargs['user']
            return render(request, template_name, {'user': user})
        else:
            return HttpResponse("Not Allowed")



class InsertNewPassword(FormView):
    template_name = 'user_auth/insert_password.html'
    form_class = InsertNewPasswordForm

    def form_valid(self, form):
        phone_number = form.cleaned_data.get('phone_number')
        user = User.objects.get(phone_number=phone_number)
        user.set_password(form.cleaned_data['password1'])
        user.save()
        return redirect('login_view')


def logout_user(request):
    logout(request)
    return redirect('login_view')


class PrivacyPolicyView(TemplateView):
    template_name = 'user_auth/privacypolicy.html'

    def get(self, request, *args, **kwargs):
        self.extra_context = {
            'privacypolicy': PrivacyPolicy.objects.first()
        }
        return super().get(request, *args, **kwargs)