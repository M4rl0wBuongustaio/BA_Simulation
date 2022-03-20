class Warehouse:
    def __init__(self, env, reorder_point, target_stock, stock):
        self.env = env
        self.reorder_point = reorder_point
        self.target_stock = target_stock
        # A list of product_batch objects.
        self.stock = stock

    def get_reorder_point(self):
        return self.reorder_point

    def get_target_stock(self):
        return self.target_stock

    def get_available_stock(self, delivery_time):
        stock = 0
        valid_batches = []
        today = self.env.now
        # Count not expired product batches only.
        for product_batch in self.stock:
            if product_batch.get_expiration_date() - delivery_time > today:
                stock = stock + product_batch.get_quantity()
                valid_batches.append(product_batch)
            else:
                continue
        self.stock = valid_batches
        return stock

    def reduce_stock(self, quantity):
        # FIFO
        index = -1
        while quantity > 0:
            if self.stock[index].get_quantity() >= quantity:
                self.stock[index].set_quantity(self.stock[index].get_quantity() - quantity)
                if self.stock[index].get_quantity() == 0:
                    self.stock.remove(self.stock[index])
            else:
                quantity = quantity - self.stock[index].get_quantity()
                self.stock.remove(self.stock[index])
                continue

    def calculate_order_quantity(self, delivery_time):
        return self.get_target_stock() - self.get_available_stock(delivery_time)

    def receive_delivery(self, product_batch):
        self.stock.append(product_batch)
