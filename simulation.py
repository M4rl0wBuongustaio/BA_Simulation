from entities import customer, wholesaler, manufacturer, raw_material_supplier
from resources import warehouse, product_batch, order
import numpy as np
import monitoring
import random
import simpy
from datetime import datetime

start = datetime.now()


def simulate(iteration):
    env = simpy.Environment()
    expiration = 20
    extension = 30

    # Raw Material Supplier
    rms = raw_material_supplier.RawMaterialSupplier(env=env, dis_start=0, dis_duration=0, durability=expiration)

    # Manufacturer
    mr_product_batch = product_batch.ProductBatch(quantity=665, production_date=0, expiration_date=expiration - 2)
    mr_stock = [mr_product_batch]
    mr_warehouse = warehouse.Warehouse(env=env, reorder_point=225, target_stock=645, stock=mr_stock)
    mr = manufacturer.Manufacturer(env=env, raw_material_supplier=rms, dis_start=0, dis_duration=0,
                                   expiration_extension=extension, warehouse=mr_warehouse, delivery_duration=2,
                                   lead_time=2,
                                   address=0)

    # Wholesaler
    ws_product_batch = product_batch.ProductBatch(quantity=445, production_date=0,
                                                  expiration_date=expiration + extension - 5)
    ws_stock = [ws_product_batch]
    ws_warehouse = warehouse.Warehouse(env=env, reorder_point=70, target_stock=445, stock=ws_stock)
    ws = wholesaler.Wholesaler(env=env, warehouse=ws_warehouse, manufacturer=mr, dis_start=0, dis_duration=0,
                               delivery_duration=1, address=1, average_demand=15)

    var_monitor = monitoring.Monitoring(ws_warehouse=ws_warehouse, mr_warehouse=mr_warehouse)

    def monitor():
        while True:
            if ws.get_daily_orders() == 0:
                ws_service_level = 1
            else:
                ws_service_level = (ws.get_daily_orders() - ws.get_daily_backorders()) / ws.get_daily_orders()
            if mr.get_daily_orders() == 0:
                mr_service_level = 1
            else:
                mr_service_level = (mr.get_daily_orders() - mr.get_daily_backorders()) / mr.get_daily_orders()
            data = {
                'iteration': iteration,
                'date': env.now,
                'mr_stock': mr_warehouse.get_available_stock(
                    delivery_duration=0,
                    remove_expired=False
                ),
                'mr_backorder': mr.get_count_backorders(),
                'mr_service_level': mr_service_level,
                'mr_depreciated_goods': mr_warehouse.get_depreciated_goods_count(),
                'ws_stock': ws_warehouse.get_available_stock(
                    delivery_duration=0,
                    remove_expired=False
                ),
                'ws_backorder': ws.get_count_backorders(),
                'ws_service_level': ws_service_level,
                'ws_depreciated_goods': ws_warehouse.get_depreciated_goods_count()
            }
            var_monitor.append_data(data=data)
            ws.reset_daily_back_orders()
            yield env.timeout(1)

    def customer_generator():
        while True:
            count_customers = int(np.random.normal(loc=15, scale=1, size=1))
            for i in range(count_customers):
                customer.Customer(env=env, quantity=1, wholesaler=ws, address=2).place_order()
            yield env.timeout(1)

    env.process(customer_generator())
    env.process(monitor())
    env.run(until=365)
    # var_monitor.save_data('scenario_0')
    var_monitor.plot()


for i in range(1):
    simulate(iteration=i)

end = datetime.now()
print(end - start)
