from resources import order, carrier, product_batch, delivery
import numpy as np
import queue


class Manufacturer:
    def __init__(self, env, raw_material_supplier, dis_start, dis_duration, dis_lead_time,
                 expiration_extension, warehouse, delivery_duration, lead_time, address):
        self.env = env
        self.raw_material_supplier = raw_material_supplier
        self.dis_start = dis_start
        self.dis_duration = dis_duration
        self.expiration_extension = expiration_extension
        self.warehouse = warehouse
        self.delivery_duration = delivery_duration
        self.lead_time = lead_time
        self.dis_lead_time = dis_lead_time
        self.address = address
        self.daily_orders = 0
        self.daily_backorders = 0
        self.delivery_pending = False
        self.backorder = queue.Queue()

    def receive_delivery(self, delivery):
        self.delivery_pending = False
        if len(delivery.get_product_batch()) > 1:
            for i in range(len(delivery.get_product_batch())):
                self.warehouse.receive_delivery(delivery.get_product_batch()[i])
        else:
            self.warehouse.receive_delivery(delivery.get_product_batch()[0])
        if not self.backorder.empty():
            self.handle_backorders()

    def receive_order(self, customer_order):
        if self.backorder.empty():
            if self.enough_stock(customer_order):
                self.env.process(self.produce(customer_order))
            elif not self.delivery_pending:
                self.add_backorder(customer_order)
                self.place_order(customer_order)
        else:
            self.add_backorder(customer_order)

    def enough_stock(self, customer_order):
        order_quantity = customer_order.get_quantity()
        customer = customer_order.get_debtor()
        available_stock = self.warehouse.get_available_stock(
            delivery_duration=(self.delivery_duration + self.lead_time - self.expiration_extension),
            remove_expired=True
        )
        if available_stock >= order_quantity:
            return True
        else:
            return False

    def handle_backorders(self):
        while not self.backorder.empty():
            backorder = self.get_last_backorder()
            if self.enough_stock(backorder):
                self.env.process(self.produce(backorder))
            else:
                self.add_backorder(backorder)
                self.place_order(backorder)
                break

    def produce(self, customer_order):
        order_quantity = customer_order.get_quantity()
        ex_date = self.warehouse.get_product_expiration_date(order_quantity)
        pro_date = self.warehouse.get_product_production_date(order_quantity)
        list_product_batch = []
        for key in ex_date.keys():
            i = 0
            pb = product_batch.ProductBatch(expiration_date=key + self.expiration_extension, quantity=ex_date[key],
                                            production_date=list(pro_date)[i]
                                            )
            list_product_batch.append(pb)
            i += 1
        var_delivery = delivery.Delivery(product_batch=list_product_batch, debtor=customer_order.get_debtor())
        self.warehouse.reduce_stock(order_quantity)
        reorder_point = self.warehouse.get_reorder_point()
        available_stock = self.warehouse.get_available_stock(
            delivery_duration=(self.delivery_duration + self.lead_time - self.expiration_extension),
            remove_expired=False
        )
        if available_stock <= reorder_point and not self.delivery_pending:
            self.env.process(self.place_scheduled_order(customer_order))
        yield self.env.timeout(abs(round(np.random.normal(loc=self.get_lead_time(), scale=1, size=1)[0])))
        self.initiate_delivery(var_delivery)

    def initiate_delivery(self, var_delivery):
        self.env.process(carrier.Carrier(self.env, delivery=var_delivery).deliver())

    def place_scheduled_order(self, customer_order):
        self.delivery_pending = True
        yield self.env.timeout(21)
        quantity = self.warehouse.calculate_order_quantity(
            delivery_duration=(self.delivery_duration + self.lead_time - self.expiration_extension),
        )
        self.raw_material_supplier.handle_order(order.Order(quantity=quantity, debtor=self))

    def place_order(self, customer_order):
        self.delivery_pending = True
        order_quantity = customer_order.get_quantity()
        customer = customer_order.get_debtor()
        quantity = self.warehouse.calculate_order_quantity(
            delivery_duration=(self.delivery_duration + self.lead_time - self.expiration_extension),
        )
        quantity += 2 * order_quantity / customer.get_average_demand()
        self.raw_material_supplier.handle_order(order.Order(quantity=quantity, debtor=self))

    def add_backorder(self, customer_order):
        self.backorder.put_nowait(customer_order)

    def get_last_backorder(self):
        return self.backorder.get_nowait()

    def get_count_backorders(self):
        return self.backorder.qsize()

    def get_address(self):
        return self.address

    def get_lead_time(self):
        if self.dis_start <= self.env.now <= (self.dis_start + self.dis_duration) and self.dis_duration > 0:
            return self.dis_lead_time
        else:
            return self.lead_time

    def get_delivery_duration(self):
        return self.delivery_duration

    def add_daily_order(self):
        self.daily_orders += 1

    def get_daily_orders(self):
        return self.daily_orders

    def reset_daily_back_orders(self):
        self.daily_orders = 0
        self.daily_backorders = 0

    def add_daily_backorder(self):
        self.daily_backorders += 1

    def get_daily_backorders(self):
        return self.daily_backorders
