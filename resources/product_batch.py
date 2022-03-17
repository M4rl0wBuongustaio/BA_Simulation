class ProductBatch:
    def __init__(self, quantity, production_date, expiration_date):
        self.quantity = quantity
        self.production_date = production_date
        self.expiration_date = expiration_date

    def get_quantity(self):
        return self.quantity

    def set_quantity(self, quantity):
        self.quantity = quantity

    def get_production_date(self):
        return self.production_date

    def get_expiration_date(self):
        return self.expiration_date

    def set_expiration_date(self, date):
        self.expiration_date = date
