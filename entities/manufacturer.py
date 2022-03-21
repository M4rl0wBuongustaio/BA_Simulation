from resources import order, carrier, product_batch, delivery
import queue


class Manufacturer:
    def __init__(self, env, raw_material_supplier, dis_start,
                 dis_duration, warehouse, delivery_duration, lead_time, address):
        self.env = env
        self.raw_material_supplier = raw_material_supplier
        self.dis_start = dis_start
        self.dis_duration = dis_duration
        self.warehouse = warehouse
        self.delivery_duration = delivery_duration
        self.lead_time = lead_time
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
            if self.enough_stock(customer_order.get_quantity()):
                self.env.process(self.produce(customer_order))
        else:
            self.add_backorder(customer_order)

    def enough_stock(self, quantity):
        available_stock = self.warehouse.get_available_stock(self.delivery_duration)
        if available_stock >= quantity:
            reorder_point = self.warehouse.get_reorder_point()
            if (available_stock - quantity) <= reorder_point and not self.delivery_pending:
                self.place_order()
            return True
        else:
            return False

    def handle_backorders(self):
        while not self.backorder.empty():
            backorder = self.get_last_backorder()
            order_quantity = backorder.get_quantity()
            if self.enough_stock(order_quantity):
                self.env.process(self.produce(backorder))
            else:
                break

    def produce(self, customer_order):
        order_quantity = customer_order.get_quantity()
        yield self.env.timeout(order_quantity / self.lead_time)
        self.initiate_delivery(customer_order)

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

    def place_order(self):
        self.delivery_pending = True
        order_quantity = self.warehouse.calculate_order_quantity(self.delivery_duration)
        self.raw_material_supplier.handle_order(order.Order(order_quantity, self))

    def add_backorder(self, customer_order):
        self.backorder.put(customer_order)

    def get_last_backorder(self):
        return self.backorder.get_nowait()

    def get_address(self):
        return self.address
