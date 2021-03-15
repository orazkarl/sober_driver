from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home_view'),
    path('ajax/getMyOrders', views.getMyOrders, name='get_my_orders'),

]
