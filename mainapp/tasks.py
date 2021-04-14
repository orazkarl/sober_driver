from background_task import background
from .models import Order



    @background(schedule=0)
def update_order_status(order_id):
    order = Order.objects.get(pk=order_id)
    order.status = 'finished'
    order.save()
    driver = order.selected_driver
    driver.is_free = True
    driver.save()