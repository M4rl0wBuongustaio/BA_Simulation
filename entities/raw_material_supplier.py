from resources import product_batch, delivery, carrier


class RawMaterialSupplier:
    def __init__(self, env, dis_start, dis_duration, expiration_date):
        self.env = env
        self.dis_start = dis_start
        self.dis_duration = dis_duration
        self.expiration_date = expiration_date

    def handle_order(self, order):
        quantity = order.get_quantity()
        debtor = order.get_debtor()
        production_date = self.env.now
        expiration_date = self.expiration_date + self.env.now
        product = product_batch.ProductBatch(
            quantity=quantity,
            production_date=production_date,
            expiration_date=expiration_date
        )
        raw_material_delivery = delivery.Delivery([product], debtor)
        self.env.process(carrier.Carrier(self.env, raw_material_delivery).deliver())