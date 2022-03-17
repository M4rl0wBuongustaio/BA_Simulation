from resources import order

class Customer:
    def __init__(self, env, quantity, wholesaler):
        self.env = env
        self.quantity = quantity
        self.wholesaler = wholesaler

    def get_quantity(self):
        return self.quantity

    def get_wholesaler(self):
        return self.wholesaler

    def get_id(self):
        return id(self)

    def place_order(self):
        self.wholesaler.receive_delivery(order.Order(self.quantity, self))

    # def receive_delivery(self):
