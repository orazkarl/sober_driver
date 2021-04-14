from django import forms
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from .models import User
from mainapp.models import City
from datetime import datetime, timedelta
from mainapp.tasks import update_user_restriction
from background_task.tasks import Task


class RegisterForm(forms.ModelForm):
    CHOICES = ((7, 'Казахстан (+7)'), (7, 'Россия (+7)'),)

    phone_number = forms.IntegerField(label='Ваш номер телефона', required=True,
                                      widget=forms.NumberInput(attrs={'placeholder': '7777777777'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}), )
    password2 = forms.CharField(label='Пароль (повторно)',
                                widget=forms.PasswordInput(attrs={'placeholder': 'Пароль (повторно)'}))
    country_code = forms.ChoiceField(label='Код страны', required=True, choices=CHOICES)
    # city = forms.ChoiceField(choices=[(city.name, city.name) for city in City.objects.all()])
    first_name = forms.CharField()
    last_name = forms.CharField()
    MIN_LENGTH = 4

    class Meta:
        model = User
        fields = ['country_code', 'phone_number', 'password1', 'password2', 'first_name', 'last_name', 'city']

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'registration-input'
            visible.field.widget.attrs['autocomplete'] = 'off'
            visible.field.widget.attrs['placeholder'] = visible.field.label

    def clean_password1(self):
        password = self.data.get('password1')
        validate_password(password)
        if password != self.data.get('password2'):
            raise forms.ValidationError("Пароли не соответствуют")
        return password

    def clean_phone_number(self):
        phone_number = self.data.get('phone_number')
        if User.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("Другой пользователь с этим номером телефона уже существует")
        return phone_number

    def save(self, *args, **kwargs):
        user = super(RegisterForm, self).save(*args, **kwargs)
        user.set_password(self.cleaned_data['password1'])
        user.avatar = self.cleaned_data.get('avatar')
        user.active_subscription = True
        user.subscription_day = datetime.now() + timedelta(days=7)
        update_user_restriction(user_id=user.id, repeat=Task.DAILY)
        user.save()
        return user


class PhoneVerificationForm(forms.Form):
    one_time_password = forms.IntegerField()

    class Meta:
        fields = ['one_time_password', ]


class LoginForm(forms.Form):
    phone_number = forms.IntegerField(label='Ваш номер телефона', required=True,
                                      widget=forms.NumberInput(attrs={'placeholder': '7777777777'}))
    password = forms.CharField()

    class Meta:
        fields = ['phone_number', 'password']

    def clean(self):
        phone_number = self.cleaned_data.get('phone_number')
        password = self.cleaned_data.get('password')
        user = authenticate(username=phone_number, password=password)
        if not user:
            raise forms.ValidationError("Извините, этот логин был недействителен. Пожалуйста, попробуйте еще раз.")
        return self.cleaned_data

    def login(self, request):
        phone_number = self.cleaned_data.get('phone_number')
        password = self.cleaned_data.get('password')
        user = authenticate(username=phone_number, password=password)
        return user


class RestorePasswordForm(forms.Form):
    country_code = forms.IntegerField()
    phone_number = forms.IntegerField(required=True)

    class Meta:
        fields = ['country_code', 'phone_number']

    def clean_phone_number(self):
        phone_number = self.data.get('phone_number')
        if not User.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError(
                "Пользователь с таким номером не существует")
        return phone_number


class RestorePasswordConfirmForm(forms.Form):
    one_time_password = forms.IntegerField()

    class Meta:
        fields = ['one_time_password', ]


class InsertNewPasswordForm(forms.Form):
    phone_number = forms.IntegerField()
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        fields = ['password1', 'password2', 'phone_number']

    def clean_password1(self):
        password = self.data.get('password1')
        validate_password(password)
        if password != self.data.get('password2'):
            raise forms.ValidationError("Пароли не соответствуют")
        return password
