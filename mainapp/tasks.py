from background_task import background
from .models import Order
from user_auth.models import User


@background(schedule=600)
def update_order_status_finished(order_id):
    order = Order.objects.get(pk=order_id)
    order.status = 'finished'
    order.save()
    driver = order.selected_driver
    driver.is_free = True
    driver.save()


@background(schedule=900)
def update_order_status_notselected(order_id):
    order = Order.objects.get(pk=order_id)
    order.status = 'notselected'
    order.save()


@background(schedule=0)
def update_user_restriction(user_id):
    user = User.objects.get(id=user_id)
    user.restriction = user.city.restriction
    user.save()
