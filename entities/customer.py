from resources import order


class Customer:
    def __init__(self, env, quantity, wholesaler, address):
        self.env = env
        self.quantity = quantity
        self.wholesaler = wholesaler
        self.address = address

    def get_quantity(self):
        return self.quantity

    def get_wholesaler(self):
        return self.wholesaler

    def get_address(self):
        return self.address

    def get_id(self):
        return id(self)

    def place_order(self):
        self.wholesaler.receive_order(order.Order(self.quantity, self))

    def receive_delivery(self, delivery):
        print(
            'Customer: ' + str(id(self)) + ' received a delivery. \n'
            + 'Expiration date: ' + str(delivery.get_product_batch().get_expiration_date()) + '\n'
            + 'Current date: ' + str(self.env.now) + '\n'
        )
