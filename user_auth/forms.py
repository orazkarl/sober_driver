from django import forms
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from .models import User
from django.core.files.images import get_image_dimensions
from mainapp.models import City
from datetime import datetime, timedelta


class RegisterForm(forms.ModelForm):
    CHOICES = ((7, 'Казахстан (+7)'), (7, 'Россия (+7)'),)

    phone_number = forms.IntegerField(label='Ваш номер телефона', required=True,
                                      widget=forms.NumberInput(attrs={'placeholder': '7777777777'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}), )
    password2 = forms.CharField(label='Пароль (повторно)',
                                widget=forms.PasswordInput(attrs={'placeholder': 'Пароль (повторно)'}))
    country_code = forms.ChoiceField(label='Код страны', required=True, choices=CHOICES)
    city = forms.ChoiceField(choices=[(city.name, city.name) for city in City.objects.all()])
    first_name = forms.CharField()
    last_name = forms.CharField()
    avatar = forms.ImageField()
    driver_license_number = forms.CharField()
    driving_experience = forms.IntegerField()
    trip_from_price = forms.IntegerField()
    trip_hour_price = forms.IntegerField()
    average_arrival = forms.IntegerField()
    knowledgecity = forms.CharField()
    bio = forms.CharField()
    iin = forms.CharField()
    front_passport = forms.ImageField()
    back_passport = forms.ImageField()
    together_passport = forms.ImageField()
    MIN_LENGTH = 4

    class Meta:
        model = User
        # fields = ['country_code', 'phone_number', 'password1', 'password2']
        fields = ['country_code', 'phone_number', 'password1', 'password2',
                  'first_name', 'last_name', 'avatar', 'driver_license_number', 'driving_experience', 'iin', 'city',
                  'trip_from_price', 'trip_hour_price','average_arrival', 'knowledgecity', 'bio', 'front_passport', 'back_passport', 'together_passport']

        # widgets = {
        #     'date_contract': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
        # }

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'registration-input'
            visible.field.widget.attrs['autocomplete'] = 'off'
            visible.field.widget.attrs['placeholder'] = visible.field.label

    # def clean_username(self):
    #     username = self.data.get('username')
    #     return username

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
        user.subscription_day = datetime.now() + timedelta(days=30)

        print('Saving user with country_code', user.country_code)
        user.save()
        return user


class PhoneVerificationForm(forms.Form):
    one_time_password = forms.IntegerField()

    class Meta:
        fields = ['one_time_password', ]


class LoginForm(forms.Form):
    phone_number = forms.IntegerField(label='Ваш номер телефона', required=True,
                                      widget=forms.NumberInput(attrs={'placeholder': '7777777777'}))
    # username = forms.CharField()
    password = forms.CharField()

    #
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
        print(1)
        password = self.data.get('password1')
        validate_password(password)
        if password != self.data.get('password2'):
            raise forms.ValidationError("Пароли не соответствуют")
        return password

    # def save(self, *args, **kwargs):
    #     user = super(InsertNewPasswordForm, self).save(*args, **kwargs)
    #     user.set_password(self.cleaned_data['password1'])
    #     # print('Saving user with country_code', user.country_code)
    #     user.save()
    #     return user
