from entities import customer, wholesaler, manufacturer, raw_material_supplier
from resources import warehouse, product_batch, order
import numpy as np
import monitoring
import random
import simpy

env = simpy.Environment()

# Raw Material Supplier
rms = raw_material_supplier.RawMaterialSupplier(env=env, dis_start=0, dis_duration=0, expiration_date=15)

# Manufacturer
mr_product_batch = product_batch.ProductBatch(quantity=500, production_date=0, expiration_date=15)
mr_stock = [mr_product_batch]
mr_warehouse = warehouse.Warehouse(env=env, reorder_point=100, target_stock=500, stock=mr_stock)
mr = manufacturer.Manufacturer(env=env, raw_material_supplier=rms, dis_start=0, dis_duration=0, warehouse=mr_warehouse,
                               delivery_duration=4, lead_time=5, address=0)

# Wholesaler
ws_product_batch = product_batch.ProductBatch(quantity=0, production_date=0, expiration_date=15)
ws_stock = [ws_product_batch]
ws_warehouse = warehouse.Warehouse(env=env, reorder_point=100, target_stock=500, stock=ws_stock)
ws = wholesaler.Wholesaler(env=env, warehouse=ws_warehouse, manufacturer=mr, dis_start=0, dis_duration=0,
                           delivery_duration=2, address=1)


def monitor(env):
    while True:
        # Data that should be monitored.
        yield env.timeout(1)


def customer_generator(env):
    while True:
        # count_customers = np.random.normal(loc=5, scale=10, size=1000)
        count_customers = 1  # random.randint(0, 15)
        while count_customers > 0:
            customer.Customer(env=env, quantity=1, wholesaler=ws, address=2).place_order()
            count_customers -= 1
        yield env.timeout(1)


# env.process(monitor(env))
env.process(customer_generator(env))
env.run(until=365)

print('Simulation successfully completed.')
