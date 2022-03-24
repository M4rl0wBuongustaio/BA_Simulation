import matplotlib.pyplot as plt
from os import path
import pandas as pd


class Monitoring:
    def __init__(self, ws_warehouse, mr_warehouse):
        self.ws_warehouse = ws_warehouse
        self.mr_warehouse = mr_warehouse
        self.data_set = pd.DataFrame()
        self.path = '/Users/leonbecker/PycharmProjects/BA_Simulation/'

    def append_data(self, data):
        self.data_set = self.data_set.append(data, ignore_index=True)

    def print_data(self):
        print(self.data_set)

    def save_data(self, name):
        if not path.exists(self.path + name):
            self.data_set.to_csv(path_or_buf=name)
        else:
            self.data_set.to_csv(path_or_buf=name, mode='a', header=False)

    def plot_inventories(self, name):
        self.data_set.plot(
            x='date',
            y=['mr_stock', 'mr_backorder'],
            kind='line',
            title='Inventory development of MANUFACTURER warehouse and backorders',
            grid=True,
            figsize=(19.2, 10.8)
        )
        plt.axhline(
            y=self.mr_warehouse.get_reorder_point(),
            c='black'
        )
        plt.savefig(name + '.pdf')
        plt.show()
        self.plot_inventories_order_dates(name)

    def plot_inventories_order_dates(self, name):
        order_dates = self.mr_warehouse.get_order_dates()
        self.data_set.plot(
            x='date',
            y=['mr_stock', 'mr_backorder'],
            kind='line',
            title='Inventory development of MANUFACTURER warehouse',
            grid=True,
            figsize=(19.2, 10.8)
        )
        plt.axhline(
            y=self.mr_warehouse.get_reorder_point(),
            c='black'
        )
        for order_date in order_dates:
            plt.axvline(
                x=order_date,
                c='gainsboro',
                linestyle='--'
            )

        plt.savefig(name + '_order_dates' + '.pdf')
        plt.show()
