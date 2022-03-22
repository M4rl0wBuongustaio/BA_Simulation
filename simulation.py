from entities import customer, wholesaler, manufacturer, raw_material_supplier
from resources import warehouse, product_batch
import numpy as np
import monitoring
import random
import simpy

# General
env = simpy.Environment()
var_monitor = monitoring.Monitoring()

# Raw Material Supplier
rms = raw_material_supplier.RawMaterialSupplier(env=env, dis_start=0, dis_duration=0, durability=15)

# Manufacturer
mr_product_batch = product_batch.ProductBatch(quantity=80, production_date=0, expiration_date=15)
mr_stock = [mr_product_batch]
mr_warehouse = warehouse.Warehouse(env=env, reorder_point=45, target_stock=80, stock=mr_stock)
mr = manufacturer.Manufacturer(env=env, raw_material_supplier=rms, dis_start=0, dis_duration=0, expiration_extension=5,
                               warehouse=mr_warehouse, delivery_duration=2, lead_time=5, address=0)

# Wholesaler
ws_product_batch = product_batch.ProductBatch(quantity=60, production_date=0, expiration_date=20)
ws_stock = [ws_product_batch]
ws_warehouse = warehouse.Warehouse(env=env, reorder_point=30, target_stock=60, stock=ws_stock)
ws = wholesaler.Wholesaler(env=env, warehouse=ws_warehouse, manufacturer=mr, dis_start=0, dis_duration=0,
                           delivery_duration=1, address=1)


def monitor(env):
    while True:
        data = {
            'iteration': 1,
            'date': env.now,
            'mr_stock': mr_warehouse.get_available_stock(delivery_time=0),
            'mr_backlog': mr.get_count_backorders(),
            'ws_stock': ws_warehouse.get_available_stock(delivery_time=0),
            'ws_backlog': ws.get_count_backorders()
        }
        var_monitor.append_data(data=data)
        yield env.timeout(1)


def customer_generator(env):
    cust = 0
    while True:
        count_customers = int(np.random.normal(loc=15, scale=4, size=1))
        while count_customers > 0:
            customer.Customer(env=env, quantity=1, wholesaler=ws, address=2).place_order()
            count_customers -= 1
        yield env.timeout(1)


# env.process(monitor(env))
env.process(customer_generator(env=env))
env.process(monitor(env=env))
env.run(until=365)

print('Simulation completed.')
var_monitor.print_data()
var_monitor.plot_inventories()
