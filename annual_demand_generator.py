import numpy as np
import pandas as pd


def annual_demand_generator(simulation_duration, w, mu, sigma):
    demand_t = 0
    T = abs(round(simulation_duration / w))
    demand_history = pd.DataFrame()

    for t in range(T):
        for s in range(5):
            for r in range(w):
                demand_t += abs(round(np.random.normal(loc=mu, scale=sigma, size=1)[0]))
            demand_history.at[s, t] = demand_t
            demand_t = 0
    annual_demand_mean = []
    for column in demand_history.columns:
        annual_demand_mean.append(abs(round(demand_history[column].mean())))
    return annual_demand_mean


print(annual_demand_generator(365, 24, 15, 2))
