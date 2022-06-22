import numpy as np

import config
from resources import carrier, order, delivery, product_batch
import queue


class Wholesaler:
    def __init__(self, env, warehouse, delivery_duration, address, average_demand, service_level, mr_list,
                 daily_resource, setup_time):
        self.env = env
        self.warehouse = warehouse
        self.delivery_duration = delivery_duration
        self.service_level = service_level
        self.mr_list = mr_list
        self.setup_time = setup_time
        self.mr_lead_time = mr_list[0].get_lead_time()
        self.mr_address = mr_list[0].get_address()
        self.daily_orders = 0
        self.daily_backorders = 0
        self.daily_shipment = 0
        self.daily_resource = daily_resource
        self.initial_daily_resource = daily_resource
        self.address = address
        self.average_demand = average_demand
        self.delivery_pending = False
        self.is_first_change = True
        self.backorder = queue.Queue()

    def receive_delivery(self, delivery):
        self.delivery_pending = False
        if len(delivery.get_product_batch()) > 1:
            for i in range(len(delivery.get_product_batch())):
                self.warehouse.receive_delivery(delivery.get_product_batch()[i])
        else:
            self.warehouse.receive_delivery(delivery.get_product_batch()[0])
        if not self.backorder.empty():
            while not self.backorder.empty():
                if self.daily_resource > 0:
                    self.handle_order(self.get_last_backorder())
                else:
                    break

    def receive_order(self, customer_order):
        self.add_daily_order()
        if self.backorder.empty() and self.daily_resource > 0:
            self.handle_order(customer_order)
        else:
            self.add_backorder(customer_order)

    def handle_order(self, customer_order):
        order_quantity = customer_order.get_quantity()
        available_stock = self.warehouse.get_available_stock(
            delivery_duration=self.delivery_duration,
            remove_expired=True
        )
        reorder_point = self.warehouse.get_reorder_point()
        if available_stock >= order_quantity:
            if (available_stock - order_quantity) < reorder_point and not self.delivery_pending:
                self.delivery_pending = True
                self.env.process(self.place_order())
            self.initiate_delivery(customer_order)
            self.use_daily_resource()
        elif not self.delivery_pending:
            self.delivery_pending = True
            self.env.process(self.place_order())
            self.add_backorder(customer_order)
        else:
            self.add_backorder(customer_order)

    def place_order(self):
        order_quantity = np.quantile(config.ANNUAL_DEMAND_WS, self.service_level)  # Minner & Transchel approach
        order_quantity += self.average_demand * (self.mr_lead_time + config.ROUTING[self.address])
        responsible_mr = yield self.env.process(self.get_responsible_manufacturer())
        responsible_mr.receive_order(order.Order(quantity=order_quantity, debtor=self))

    def initiate_delivery(self, customer_order):
        self.add_daily_shipment()
        ex_date = self.warehouse.get_product_expiration_date(customer_order.get_quantity())
        pro_date = self.warehouse.get_product_production_date(customer_order.get_quantity())
        var_product_batches = []
        for key in ex_date.keys():
            i = 0
            pb = product_batch.ProductBatch(
                quantity=ex_date[key],
                expiration_date=key,
                production_date=list(pro_date)[i]
            )
            var_product_batches.append(pb)
            i += 1
        delivery_details = delivery.Delivery(product_batch=var_product_batches, debtor=customer_order.get_debtor())
        self.warehouse.reduce_stock(customer_order.get_quantity())
        self.env.process(carrier.Carrier(self.env, delivery=delivery_details).deliver())

    def get_responsible_manufacturer(self):
        if len(self.mr_list) == 1:
            yield self.env.timeout(0)
            return self.mr_list[0]
        for i in range(len(self.mr_list)):
            if self.mr_list[i].get_lead_time() == self.mr_lead_time:
                if i > 0 and self.is_first_change:
                    self.is_first_change = False
                    yield self.env.timeout(self.setup_time)
                    return self.mr_list[i]
                else:
                    yield self.env.timeout(0)
                    return self.mr_list[i]

    def add_backorder(self, customer_order):
        self.add_daily_backorder()
        self.backorder.put_nowait(customer_order)

    def get_last_backorder(self):
        return self.backorder.get_nowait()

    def get_count_backorders(self):
        return self.backorder.qsize()

    def get_address(self):
        return self.address

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

    def get_average_demand(self):
        return self.average_demand

    def get_service_level(self):
        return self.service_level

    def reset_daily_resource(self):
        self.daily_resource = self.initial_daily_resource
        while not self.backorder.empty() and not self.delivery_pending:
            if self.daily_resource > 0:
                self.handle_order(self.get_last_backorder())
            else:
                break

    def use_daily_resource(self):
        self.daily_resource -= 1

    def add_daily_shipment(self):
        self.daily_shipment += 1

    def get_daily_shipment(self):
        return self.daily_shipment

    def reset_daily_shipment(self):
        self.daily_shipment = 0
