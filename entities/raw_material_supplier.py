from resources import product_batch, delivery, carrier


class RawMaterialSupplier:
    def __init__(self, env, dis_start, dis_duration, durability):
        self.env = env
        self.dis_start = dis_start
        self.dis_duration = dis_duration
        self.durability = durability

    def handle_order(self, order):
        quantity = order.get_quantity()
        debtor = order.get_debtor()
        production_date = self.env.now
        expiration_date = self.durability + self.env.now
        products = product_batch.ProductBatch(
            quantity=quantity,
            production_date=production_date,
            expiration_date=expiration_date
        )
        raw_material_delivery = delivery.Delivery(products, debtor)
        self.env.process(carrier.Carrier(self.env, raw_material_delivery).deliver())
