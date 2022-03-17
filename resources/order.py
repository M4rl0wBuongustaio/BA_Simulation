class Order:
    def __init__(self, quantity, debtor):
        self.quantity = quantity
        self.debtor = debtor

    def get_quantity(self):
        return self.quantity

    def get_debtor(self):
        return self.debtor
