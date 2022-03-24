class Warehouse:
    def __init__(self, env, reorder_point, target_stock, stock):
        self.env = env
        self.reorder_point = reorder_point
        self.target_stock = target_stock
        # A list of product_batch objects.
        self.stock = stock
        self.order_date = []

    def get_reorder_point(self):
        return self.reorder_point

    def get_target_stock(self):
        return self.target_stock

    def get_available_stock(self, delivery_time):
        if not self.stock:
            return 0
        stock = 0
        valid_batches = []
        today = self.env.now
        # Count not expired product batches only.
        for product_batch in self.stock:
            if (product_batch.get_expiration_date() - delivery_time) >= today:
                stock += product_batch.get_quantity()
                valid_batches.append(product_batch)
            else:
                continue
        self.stock = valid_batches
        return stock

    def get_product_expiration_date(self):
        return self.stock[-1].get_expiration_date()

    def get_product_production_date(self):
        return self.stock[-1].get_production_date()

    def reduce_stock(self, quantity):
        # FIFO
        while quantity > 0:
            if self.stock[-1].get_quantity() >= quantity:
                self.stock[-1].set_quantity(self.stock[-1].get_quantity() - quantity)
                if self.stock[-1].get_quantity() == 0 and self.env.now > self.stock[-1].get_expiration_date():
                    self.stock.remove(self.stock[-1])
                break
            else:
                quantity = quantity - self.stock[-1].get_quantity()
                self.stock.remove(self.stock[-1])
                continue

    def calculate_order_quantity(self, delivery_time):
        order_quantity = self.get_target_stock() - self.get_available_stock(delivery_time)
        self.mark_order_date()
        return order_quantity

    def receive_delivery(self, product_batch):
        self.stock.append(product_batch)

    def mark_order_date(self):
        self.order_date.append(self.env.now)

    def get_order_dates(self):
        return self.order_date
