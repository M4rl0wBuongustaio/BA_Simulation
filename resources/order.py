class Order:
    def __init__(self, quantity, debtor):
        if quantity <= 0:
            raise ValueError('Order quantity must be greater 0!')
        else:
            self.quantity = quantity
            self.debtor = debtor

    def get_quantity(self):
        return self.quantity

    def get_debtor(self):
        return self.debtor
