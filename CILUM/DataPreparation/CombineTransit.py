import numpy as np
import pandas as pd
import os

#N = 2550 #Number of zones

#Define files to combine
#wd = r'I:\000JFLOOD\Cube Land\Data\2025 Forecasts\2025 LU1H Skims'

def main(wd):
    eb_file = os.path.join(wd, 'BRT.csv')
    lb_file = os.path.join(wd, 'LocalBus.csv')

    #Read in data, and fill null values with infinity
    eb = pd.DataFrame.from_csv(eb_file).fillna(np.inf)
    lb = pd.DataFrame.from_csv(lb_file).fillna(np.inf)
    N = eb.shape[0]

    #Convert skims into NumPy arrays, and reshape so they are one-dimensional
    eb_array = np.array(eb)
    lb_array = np.array(lb)

    eb_array = np.reshape(eb_array, N**2)
    lb_array = np.reshape(lb_array, N**2)

    #Create series with zipped arrays, and then another series with the minimum time
    series = pd.Series(zip(eb_array, lb_array))
    bus_series = series.apply(min)

    #Create array from minimized array, and reshape into proper shape
    bus_array = np.array(bus_series)
    bus_array = np.reshape(bus_array, (N, N))

    #Place elements of 2D array into skim, and write to file
    transit = pd.DataFrame(bus_array, eb.index, eb.columns).replace(np.inf, np.nan)
    transit.to_csv(os.path.join(wd, 'Transit.csv'))

if __name__ == '__main__':

    wd = r'I:\000JFLOOD\Cube Land\Data\2045 Forecasts\2045 LU1 Skims'
    main(wd)
