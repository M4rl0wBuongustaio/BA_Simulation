from resources import order, carrier, product_batch, delivery
import queue


class Manufacturer:
    def __init__(self, env, raw_material_supplier, dis_start, dis_duration,
                 expiration_extension, warehouse, delivery_duration, lead_time, address):
        self.env = env
        self.raw_material_supplier = raw_material_supplier
        self.dis_start = dis_start
        self.dis_duration = dis_duration
        self.expiration_extension = expiration_extension
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
            elif not self.delivery_pending:
                self.add_backorder(customer_order)
                self.place_order()
        else:
            self.add_backorder(customer_order)

    def enough_stock(self, quantity):
        available_stock = self.warehouse.get_available_stock(self.delivery_duration - self.expiration_extension)
        if available_stock >= quantity:
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
                self.add_backorder(backorder)
                break

    def produce(self, customer_order):
        order_quantity = customer_order.get_quantity()
        new_ex_date = self.warehouse.get_product_expiration_date() + self.expiration_extension
        initial_pro_date = self.warehouse.get_product_production_date()
        self.warehouse.reduce_stock(order_quantity)
        reorder_point = self.warehouse.get_reorder_point()
        available_stock = self.warehouse.get_available_stock(self.delivery_duration - self.expiration_extension)
        if available_stock <= reorder_point and not self.delivery_pending:
            self.place_order()
        yield self.env.timeout(self.lead_time)
        self.initiate_delivery(customer_order=customer_order, expiration_date=new_ex_date,
                               production_date=initial_pro_date)

    def initiate_delivery(self, customer_order, expiration_date, production_date):
        product = product_batch.ProductBatch(
            quantity=customer_order.get_quantity(),
            expiration_date=expiration_date,
            production_date=production_date
        )
        delivery_details = delivery.Delivery(product_batch=product, debtor=customer_order.get_debtor())
        self.env.process(carrier.Carrier(self.env, delivery=delivery_details).deliver())

    def place_order(self):
        self.delivery_pending = True
        order_quantity = self.warehouse.calculate_order_quantity(self.delivery_duration)
        self.raw_material_supplier.handle_order(order.Order(order_quantity, self))

    def add_backorder(self, customer_order):
        self.backorder.put_nowait(customer_order)

    def get_last_backorder(self):
        return self.backorder.get_nowait()

    def get_count_backorders(self):
        return self.backorder.qsize()

    def get_address(self):
        return self.address
