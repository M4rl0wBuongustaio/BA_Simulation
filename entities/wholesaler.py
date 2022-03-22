import queue
from resources import carrier, order, delivery, product_batch


class Wholesaler:
    def __init__(self, env, warehouse, manufacturer, dis_start, dis_duration, delivery_duration, address):
        self.env = env
        self.warehouse = warehouse
        self.manufacturer = manufacturer
        self.dis_start = dis_start
        self.dis_duration = dis_duration
        self.delivery_duration = delivery_duration
        self.address = address
        self.delivery_pending = False
        self.backorder = queue.Queue()

    def receive_delivery(self, delivery):
        self.delivery_pending = False
        self.warehouse.receive_delivery(delivery.get_product_batch())
        if not self.backorder.empty():
            self.handle_backorders()

    def receive_order(self, customer_order):
        if self.backorder.empty():
            self.handle_order(customer_order)
        else:
            self.add_backorder(customer_order)

    def handle_order(self, customer_order):
        order_quantity = customer_order.get_quantity()
        available_stock = self.warehouse.get_available_stock(self.delivery_duration)
        reorder_point = self.warehouse.get_reorder_point()
        if available_stock >= order_quantity:
            if (available_stock - order_quantity) <= reorder_point and not self.delivery_pending:
                self.place_order()
            self.initiate_delivery(customer_order)
        elif not self.delivery_pending:
            self.place_order()
            self.add_backorder(customer_order)
        else:
            self.add_backorder(customer_order)

    def handle_backorders(self):
        available_stock = self.warehouse.get_available_stock(self.delivery_duration)
        reorder_point = self.warehouse.get_reorder_point()
        while not self.backorder.empty():
            customer_order = self.get_last_backorder()
            order_quantity = customer_order.get_quantity()
            if available_stock >= order_quantity:
                if (available_stock - order_quantity) <= reorder_point and not self.delivery_pending:
                    self.place_order()
                self.initiate_delivery(customer_order)
                available_stock -= order_quantity
            elif not self.delivery_pending:
                self.add_backorder(customer_order)
                self.place_order()
                break
            else:
                self.add_backorder(customer_order)
                break

    def place_order(self):
        self.delivery_pending = True
        order_quantity = self.warehouse.calculate_order_quantity(self.delivery_duration)
        self.manufacturer.receive_order(order.Order(quantity=order_quantity, debtor=self))

    def initiate_delivery(self, customer_order):
        ex_date = self.warehouse.get_product_expiration_date()
        pro_date = self.warehouse.get_product_production_date()
        product = product_batch.ProductBatch(
            quantity=customer_order.get_quantity(),
            expiration_date=ex_date,
            production_date=pro_date
            )
        delivery_details = delivery.Delivery(product_batch=product, debtor=customer_order.get_debtor())
        self.warehouse.reduce_stock(customer_order.get_quantity())
        self.env.process(carrier.Carrier(self.env, delivery=delivery_details).deliver())

    def add_backorder(self, customer_order):
        self.backorder.put_nowait(customer_order)

    def get_last_backorder(self):
        return self.backorder.get_nowait()

    def get_count_backorders(self):
        return self.backorder.qsize()

    def get_address(self):
        return self.address
