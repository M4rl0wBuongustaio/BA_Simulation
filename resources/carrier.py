from config import ROUTING
import numpy as np


class Carrier:
    def __init__(self, env, delivery):
        self.env = env
        self.delivery = delivery

    def deliver(self):
        debtor_address = self.delivery.get_debtor().get_address()
        for rout in ROUTING.keys():
            if rout == debtor_address:
                yield self.env.timeout(
                    abs(int(np.random.normal(loc=ROUTING[rout], scale=1, size=1)))
                )
                self.delivery.get_debtor().receive_delivery(self.delivery)
                break
