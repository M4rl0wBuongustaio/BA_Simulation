class Carrier:
    def __init__(self, env, order):
        self.env = env
        self.order = order

    def deliver(self):
        # TODO: Set up delivery.
        self.order.get_debtor()