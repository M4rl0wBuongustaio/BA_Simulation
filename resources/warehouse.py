class Warehouse:
    def __init__(self, env, reorder_point, target_stock, stock):
        self.env = env
        self.reorder_point = reorder_point
        self.target_stock = target_stock
        # A list of product_batch objects.
        self.stock = stock
        self.order_date = []
        self.depreciated_goods = 0

    def get_reorder_point(self):
        return self.reorder_point

    def get_target_stock(self):
        return self.target_stock

    def get_available_stock(self, delivery_duration, remove_expired):
        if not self.stock:
            return 0
        stock = 0
        valid_batches = []
        today = self.env.now
        # Count not expired product batches only.
        for product_batch in self.stock:
            if (product_batch.get_expiration_date() - delivery_duration) > today:  # = today:
                stock += product_batch.get_quantity()
                if remove_expired:
                    valid_batches.append(product_batch)
            elif remove_expired:
                self.depreciated_goods += product_batch.get_quantity()
            else:
                continue
        if remove_expired:
            self.stock = valid_batches
        return stock

    def get_product_expiration_date(self, quantity):
        ex_date = {}
        index = 0
        while True:
            if self.stock[index].get_quantity() >= quantity:
                ex_date[self.stock[index].get_expiration_date()] = quantity
                return ex_date
            elif self.stock[index].get_quantity() > 0:
                ex_date[self.stock[index].get_expiration_date()] = self.stock[index].get_quantity()
                quantity -= self.stock[index].get_quantity()
                index += 1
                continue
            elif self.stock[index].get_quantity() >= 0:
                index += 1
                continue

    def get_product_production_date(self, quantity):
        pro_date = {}
        index = 0
        while True:
            if self.stock[index].get_quantity() >= quantity:
                pro_date[self.stock[index].get_production_date()] = quantity
                return pro_date
            elif self.stock[index].get_quantity() > 0:
                pro_date[self.stock[index].get_production_date()] = self.stock[index].get_quantity()
                quantity -= self.stock[index].get_quantity()
                index += 1
                continue
            elif self.stock[index].get_quantity() >= 0:
                index += 1
                continue

    def reduce_stock(self, quantity):
        # FIFO
        while quantity > 0:
            if self.stock[0].get_quantity() >= quantity:
                self.stock[0].set_quantity(self.stock[0].get_quantity() - quantity)
                if self.stock[0].get_quantity() == 0 and self.env.now > self.stock[0].get_expiration_date():
                    self.stock.remove(self.stock[0])
                break
            else:
                quantity = quantity - self.stock[0].get_quantity()
                self.stock.remove(self.stock[0])
                continue

    def calculate_order_quantity(self, delivery_duration):
        order_quantity = self.get_target_stock() - self.get_available_stock(
            delivery_duration=delivery_duration,
            remove_expired=False
        )
        self.mark_order_date()
        return order_quantity

    def receive_delivery(self, product_batch):
        self.stock.append(product_batch)

    def mark_order_date(self):
        self.order_date.append(self.env.now)

    def get_order_dates(self):
        return self.order_date

    def get_depreciated_goods_count(self):
        return self.depreciated_goods
