from entities import customer, wholesaler, manufacturer, raw_material_supplier
from resources import warehouse, product_batch, order
import monitoring
import simpy


def monitor(env):
    while True:
        # Data that should be monitored.
        yield env.timeout(1)


def customer_generator(env):
    # Normaldistribution
    while True:
        return
        # i -= 1


env = simpy.Environment()
env.process(monitor(env))
env.process(customer_generator(env))
env.run(until=365)

