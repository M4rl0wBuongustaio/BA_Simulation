import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math


def load_dataframe(file_path):
    return pd.read_csv(file_path)


def average_iterations(df, iteration, var_ci_coefficient):
    mean_df = pd.DataFrame()  # columns=df.drop(columns=['iteration']).columns)
    for date in np.unique(df['date']):
        for column in df.drop(columns=['iteration', 'date']).columns:
            mean_df.at[date, 'date'] = date
            mean_df.at[date, column] = var_mean = df[column].loc[
                df['date'] == date
                ].mean().round(decimals=1)
            mean_df.at[date, column + '_std'] = var_std = df[column].loc[
                df['date'] == date
                ].std()
            mean_df.at[date, column + '_25q'] = df[column].loc[
                df['date'] == date
                ].quantile(q=0.25)
            mean_df.at[date, column + '_75q'] = df[column].loc[
                df['date'] == date
                ].quantile(q=0.75)
            mean_df.at[date, column + '_ci_up'] = (
                    var_mean + var_ci_coefficient * (var_std / math.sqrt(iteration)))
            mean_df.at[date, column + '_ci_low'] = (
                    var_mean - var_ci_coefficient * (var_std / math.sqrt(iteration)))
    mean_df = mean_df[mean_df.columns.drop(list(mean_df.filter(regex='Unnamed')))]
    return mean_df


def plot_inventories(name, df, title):
    df.plot(
        x='date',
        y=['ws_stock', 'ws_backorder'],
        kind='line',
        title=title,
        grid=True,
        figsize=(19.2, 10.8)
    )
    plt.axhline(
        y=150,
        c='black'
    )
    plt.savefig(name + '.pdf')
    plt.show()


def save_data(df, name):
    df.to_csv(name)


df = load_dataframe('scenario_0')
# 1.96 confidence interval coefficient for 95%
df = average_iterations(df, iteration=100, var_ci_coefficient=1.96)
save_data(df=df, name='scenario_0_averaged_sl_0.9')

df = load_dataframe('delivery_data_s0')
# 1.96 confidence interval coefficient for 95%
df = average_iterations(df, iteration=100, var_ci_coefficient=1.96)
save_data(df=df, name='delivery_data_s0_averaged_sl_0.9')
