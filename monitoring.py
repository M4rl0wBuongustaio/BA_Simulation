import matplotlib.pyplot as plt
from os import path
import pandas as pd
import numpy as np


class Monitoring:
    def __init__(self, ws_warehouse, mr_warehouse):
        self.ws_warehouse = ws_warehouse
        self.mr_warehouse = mr_warehouse
        self.data_set = pd.DataFrame()
        self.path = '/Users/leonbecker/PycharmProjects/BA_Simulation/'

    def append_data(self, data):
        self.data_set = pd.concat([self.data_set, pd.DataFrame.from_dict(data)])

    def print_data(self):
        print(self.data_set)

    def get_data_set(self):
        return self.data_set

    def save_data(self, name, df):
        if not path.exists(self.path + name):
            df.to_csv(path_or_buf=name)
        else:
            df.to_csv(path_or_buf=name, mode='a', header=False)

    def plot(self):
        self.data_set.plot(
            x='date',
            y='mr_depreciated_goods',
            kind='line',
            grid=True,
            figsize=(19.2, 10.8)
        )
        plt.xticks(np.arange(0, 365, 30))
        plt.show()
        self.plot_2()

    def plot_2(self):
        self.data_set.plot(
            x='date',
            y='ws_depreciated_goods',
            kind='line',
            grid=True,
            figsize=(19.2, 10.8)
        )
        plt.xticks(np.arange(0, 365, 30))
        plt.show()
        self.plot_3()

    def plot_3(self):
        self.data_set.plot(
            x='date',
            y=['mr_stock', 'mr_backorder'],
            kind='line',
            grid=True,
            figsize=(19.2, 10.8)
        )
        plt.xticks(np.arange(0, 365, 30))
        plt.show()
        self.plot_4()

    def plot_4(self):
        self.data_set.plot(
            x='date',
            y=['ws_stock', 'ws_backorder'],
            kind='line',
            grid=True,
            figsize=(19.2, 10.8)
        )
        plt.xticks(np.arange(0, 365, 30))
        plt.show()

