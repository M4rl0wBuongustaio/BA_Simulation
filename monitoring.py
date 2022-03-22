import matplotlib.pyplot as plt
import pandas as pd


class Monitoring:
    def __init__(self):
        self.data_set = pd.DataFrame()

    def append_data(self, data):
        self.data_set = self.data_set.append(data, ignore_index=True)

    def print_data(self):
        print(self.data_set)

    def save_data(self, name):
        self.data_set.to_excel(name)

    def plot_inventories(self):
        self.data_set.plot(
            x='date',
            y='ws_stock',
            kind='line',
            grid=True
        )
        plt.show()
