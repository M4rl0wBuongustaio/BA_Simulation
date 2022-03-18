import queue
from resources import carrier, order

class Wholesaler:
    def __init__(self, env, warehouse, manufacturer, dis_start, dis_duration, delivery_duration):
        self.env = env
        self.warehouse = warehouse
        self.manufacturer = manufacturer
        self.dis_start = dis_start
        self.dis_duration = dis_duration
        self.delivery_duration = delivery_duration
        self.backorder = queue.Queue()

    def receive_delivery(self, delivery):
        self.warehouse.receive_delivery(delivery.get_product_batch())
        # TODO: produce according to backorders.

    def receive_order(self, customer_order):
        if self.warehouse.get_available_stock(self.mean_delivery_time) >= customer_order.get_quantity():
            self.initiate_delivery(customer_order)
        else:
            self.initiate_order()

    def initiate_order(self):
        order_quantity = self.warehouse.calculate_order_quantity()
        self.manufacturer.receive_order(order.Order(order_quantity, self))

    def initiate_delivery(self, customer_order):
        self.env.process(carrier.Carrier(self.env, customer_order).deliver(self.delivery_duration))

    def add_backorder(self, customer_order):
        self.backorder.put(customer_order)

    def get_last_backorder(self):
        self.backorder.get_nowait()
