class Carrier:
    def __init__(self, env, order):
        self.env = env
        self.order = order

    def deliver(self, delivery_duration):
        # TODO: Set up delivery.
        yield self.env.timeout(delivery_duration)
        self.order.get_debtor().receive_delivery()
