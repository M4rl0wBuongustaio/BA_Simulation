from entities import customer, wholesaler, manufacturer, raw_material_supplier
from resources import warehouse, product_batch
import numpy as np
import monitoring
import random
import simpy


def simulate(iteration):
    env = simpy.Environment()
    expiration = 20
    extension = 10

    # Raw Material Supplier
    rms = raw_material_supplier.RawMaterialSupplier(env=env, dis_start=0, dis_duration=0, durability=expiration)

    # Manufacturer
    mr_product_batch = product_batch.ProductBatch(quantity=250, production_date=0, expiration_date=expiration)
    mr_stock = [mr_product_batch]
    mr_warehouse = warehouse.Warehouse(env=env, reorder_point=150, target_stock=250, stock=mr_stock)
    mr = manufacturer.Manufacturer(env=env, raw_material_supplier=rms, dis_start=0, dis_duration=0,
                                   expiration_extension=extension, warehouse=mr_warehouse, delivery_duration=2,
                                   lead_time=5,
                                   address=0)

    # Wholesaler
    ws_product_batch = product_batch.ProductBatch(quantity=250, production_date=0,
                                                  expiration_date=expiration + extension)
    ws_stock = [ws_product_batch]
    ws_warehouse = warehouse.Warehouse(env=env, reorder_point=150, target_stock=250, stock=ws_stock)
    ws = wholesaler.Wholesaler(env=env, warehouse=ws_warehouse, manufacturer=mr, dis_start=0, dis_duration=0,
                               delivery_duration=1, address=1)

    var_monitor = monitoring.Monitoring(ws_warehouse=ws_warehouse, mr_warehouse=mr_warehouse)

    def monitor(env, iteration):
        while True:
            data = {
                'iteration': iteration,
                'date': env.now,
                'mr_stock': mr_warehouse.get_available_stock(delivery_time=0),
                'mr_backorder': mr.get_count_backorders(),
                'ws_stock': ws_warehouse.get_available_stock(delivery_time=0),
                'ws_backorder': ws.get_count_backorders()
            }
            var_monitor.append_data(data=data)
            yield env.timeout(1)

    def customer_generator(env):
        while True:
            count_customers = int(np.random.normal(loc=15, scale=4, size=1))
            while count_customers > 0:
                customer.Customer(env=env, quantity=1, wholesaler=ws, address=2).place_order()
                count_customers -= 1
            yield env.timeout(1)

    env.process(customer_generator(env=env))
    env.process(monitor(env=env, iteration=iteration))
    env.run(until=365)
    var_monitor.save_data('scenario_0')


for i in range(100):
    simulate(iteration=i)
