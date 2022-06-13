import pandas as pd

import config
from entities import customer, wholesaler, manufacturer, raw_material_supplier
from resources import warehouse, product_batch
import numpy as np
import monitoring
import simpy
from datetime import datetime

start = datetime.now()


def simulate(iteration, mr_attributes):
    env = simpy.Environment()
    expiration = 10
    extension = 20
    delivery_data = [[0], [0], [0]]
    # Demand
    mu, sigma = 15, 2
    # Store manufacturers.
    mr_list = []

    # Raw Material Supplier
    rms = raw_material_supplier.RawMaterialSupplier(env=env, dis_start=0, dis_duration=0, expiration_date=expiration)

    # Manufacturer
    mr_lead_time = 2
    mr_product_batch = product_batch.ProductBatch(quantity=0, production_date=0, expiration_date=0 + expiration)
    mr_stock = [mr_product_batch]
    mr_warehouse = warehouse.Warehouse(env=env, reorder_point=5, target_stock=420, stock=mr_stock)

    def manufacturer_generator():
        for count in range(len(mr_attributes)):
            mr = manufacturer.Manufacturer(env=env, raw_material_supplier=rms, dis_start=mr_attributes[count][0],
                                           dis_duration=mr_attributes[count][1], expiration_extension=extension,
                                           warehouse=mr_warehouse, lead_time=mr_lead_time,
                                           dis_lead_time=mr_attributes[count][2], address=0, service_level=0.9)
            mr_list.append(mr)

    # Initiate generation of manufacturers.
    manufacturer_generator()

    # Wholesaler
    ws_address = 1
    ws_average_demand = mu
    ws_service_level = 0.9
    ws_initial_stock = np.quantile(config.ANNUAL_DEMAND_WS, ws_service_level)
    ws_initial_stock += ws_average_demand * (mr_lead_time + config.ROUTING[ws_address])
    ws_product_batch = product_batch.ProductBatch(quantity=ws_initial_stock, production_date=0,
                                                  expiration_date=expiration + extension - 6)
    ws_stock = [ws_product_batch]
    ws_warehouse = warehouse.Warehouse(env=env, reorder_point=105, target_stock=450, stock=ws_stock)
    ws = wholesaler.Wholesaler(env=env, warehouse=ws_warehouse, dis_start=0, dis_duration=0,
                               delivery_duration=1, address=ws_address, average_demand=ws_average_demand,
                               service_level=ws_service_level, mr_list=mr_list, daily_resource=2*ws_average_demand)

    var_monitor = monitoring.Monitoring(ws_warehouse=ws_warehouse, mr_warehouse=mr_warehouse)

    def monitor():
        while True:
            if ws.get_daily_orders() == 0:
                ws_service_level = 1
            else:
                ws_service_level = (ws.get_daily_orders() - ws.get_daily_backorders()) / ws.get_daily_orders()
            data = {
                'iteration': [iteration],
                'date': [env.now],
                'ws_stock': [ws_warehouse.get_available_stock(
                    delivery_duration=0,
                    remove_expired=False
                )],
                'ws_backorder': [ws.get_count_backorders()],
                'ws_service_level': [ws_service_level],
                'ws_depreciated_goods': [ws_warehouse.get_depreciated_goods_count()]
            }
            for count in range(len(mr_list)):
                if mr_list[count].get_daily_orders() == 0:
                    mr_service_level = 1
                else:
                    mr_service_level = (mr_list[count].get_daily_orders() - mr_list[count].get_daily_backorders()) / \
                                       mr_list[count].get_daily_orders()
                mr_data = {'mr' + str(count) + '_backorder': [mr_list[count].get_count_backorders()],
                           'mr' + str(count) + '_service_level': [mr_service_level],
                           'mr' + str(count) + '_depreciated_goods': [
                               mr_list[count].get_warehouse().get_depreciated_goods_count()],
                           'mr' + str(count) + '_stock': [mr_list[count].get_warehouse().get_available_stock(
                               delivery_duration=0,
                               remove_expired=False
                           )]}
                data.update(mr_data)
            var_monitor.append_data(data=data)
            ws.reset_daily_back_orders()
            yield env.timeout(1)

    def customer_generator():
        while True:
            count_customers = abs(round(np.random.normal(loc=mu, scale=sigma, size=1)[0]))
            for i in range(count_customers):
                customer.Customer(
                    env=env, quantity=1, wholesaler=ws, address=2, delivery_monitoring=delivery_data,
                    iteration=iteration
                ).place_order()
            yield env.timeout(1)
            # Reset daily resource for wholesaler after each day.
            ws.reset_daily_resource()


    env.process(customer_generator())
    env.process(monitor())
    env.run(until=365)
    var_monitor.save_data(df=pd.DataFrame(
        {
            'iteration': delivery_data[0],
            'date': delivery_data[1],
            'expiration_date': delivery_data[2]
        }
    ), name='delivery_data_s0')
    var_monitor.save_data(name='scenario_0', df=var_monitor.get_data_set())
    # var_monitor.plot()
    # print(ws_warehouse.get_order_dates())
    # print(mr_warehouse.get_order_dates())


# Structure: {id: [dis_start, dis_duration, dis_lead_time]}
mr_attributes = {
    0: [0, 0, 0],
    # 1: [0, 0, 0]
}

for i in range(1):
    simulate(iteration=i, mr_attributes=mr_attributes)

end = datetime.now()
print(end - start)
