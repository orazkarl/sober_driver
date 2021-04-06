from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name ='register_view'),
    path('login/', views.LoginView.as_view(), name ='login_view'),
    path('verify/', views.PhoneVerificationView, name='verify_view'),
    path('password/restore', views.RestorePasswordView.as_view(), name='restore_password'),
    path('password/restore/confirm', views.RestorePasswordConfirmView, name='restore_password_confirm'),
    path('password/insert', views.InsertNewPassword.as_view(), name='insert_new_password'),
    path('logout/', views.logout_user, name='logout'),
path('privacypolicy/', views.PrivacyPolicyView.as_view(), name='privacypolicy'),
]
