from django.urls import path
from . import views
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
urlpatterns = [
    path('profile/', views.ProfileView.as_view(), name='profile_view'),
    path('orders/', views.OrdersView.as_view(), name='orders_view'),
    path('order/detail/<int:pk>', views.OrderDetailView.as_view(), name='order_detail'),
    path('ajax/getOrders', views.getOrders, name='get_orders'),
    path('instruction/', views.InstructionView.as_view(), name='instruction_view'),
    path('settings/', views.SettingsView.as_view(), name='settings_view'),
path('anketa/', views.AnketaView.as_view(), name='anketa_view'),
    path('password-change/', PasswordChangeView.as_view(), name='password_change'),
    path('password-change/done', PasswordChangeDoneView.as_view(), name='password_change_done'),

]
