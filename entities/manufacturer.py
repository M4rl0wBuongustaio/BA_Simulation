import queue


class Manufacturer:
    def __init__(self, raw_material_supplier, dis_start, dis_duration):
        self.raw_material_supplier = raw_material_supplier
        self.dis_start = dis_start
        self.dis_duration = dis_duration
        self.backorder = queue.Queue()

    def receive_delivery(self):
        return
        # Do something.

    def receive_order(self, order):
        return
