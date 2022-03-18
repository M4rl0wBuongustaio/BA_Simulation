class Delivery:
    def __init__(self, product_batch, debtor):
        self.product_batch = product_batch
        self.debtor = debtor

    def get_product_batch(self):
        return self.product_batch

    def get_debtor(self):
        return self.debtor
