from resources import order, carrier
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
            self.env.process(self.backorder_production())

    def receive_order(self, customer_order):
        if self.backorder.empty():
            self.env.process(self.standard_production(customer_order))
        else:
            self.add_backorder(customer_order)

    def backorder_production(self):
        while not self.backorder.empty():
            customer_order = self.get_last_backorder()
            order_quantity = customer_order.get_quantity()
            available_quantity = self.warehouse.get_available_stock(self.delivery_duration)
            if available_quantity >= order_quantity:
                if (available_quantity - order_quantity) < self.warehouse.get_reorder_point() \
                        and not self.delivery_pending:
                    self.place_order()
                self.warehouse.reduce_stock(order_quantity)
                yield self.env.timeout(order_quantity / self.lead_time)
                self.initiate_delivery(customer_order)
            elif not self.delivery_pending:
                self.add_backorder(customer_order)
                self.place_order()
                break
            else:
                self.add_backorder(customer_order)
                break

    def standard_production(self, customer_order):
        order_quantity = customer_order.get_quantity()
        available_quantity = self.warehouse.get_available_stock(self.delivery_duration)
        if available_quantity >= order_quantity:
            if (available_quantity - order_quantity) < self.warehouse.get_reorder_point() \
                    and not self.delivery_pending:
                self.place_order()
            self.warehouse.reduce_stock(order_quantity)
            yield self.env.timeout(order_quantity / self.lead_time)
            self.initiate_delivery(customer_order)
        elif not self.delivery_pending:
            self.add_backorder(customer_order)
            self.place_order()
        else:
            self.add_backorder(customer_order)

    def initiate_delivery(self, customer_order):
        self.env.process(carrier.Carrier(self.env, customer_order).deliver())

    def place_order(self):
        self.delivery_pending = True
        order_quantity = self.warehouse.calculate_order_quantity()
        self.raw_material_supplier.handle_order(order.Order(order_quantity, self))

    def add_backorder(self, customer_order):
        self.backorder.put(customer_order)

    def get_last_backorder(self):
        return self.backorder.get_nowait()

    def get_address(self):
        return self.address
