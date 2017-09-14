from __future__ import division
import arcpy
import pandas as pd
import numpy as np

#averaging = True
#n = 2

#infile = r'P:\MPO\40 RTP and Air Quality\2045 LRTP\08_LandUseModel_Forecasting\Land Use Model Runs\BaseYearIncome\Initial2025Run3M\FILES\EndogVarOut.csv' #Contains endogenous variables
#outfile = r'P:\MPO\40 RTP and Air Quality\2045 LRTP\08_LandUseModel_Forecasting\Land Use Model Runs\BaseYearIncome\Initial2025Run3M\MODEL\Inputs\ZONES.dbf' #Places endogenous variables

def main(infile, outfile, n):

    #Read in input data
    data = pd.DataFrame.from_csv(infile, index_col = None)
    fields = data.columns.tolist()
    data = data.set_index('IDZONE')

    #Update zonal file with averaged values or input values themselves depending on what the user selects
    zones = arcpy.da.UpdateCursor(outfile, fields)
    for zone in zones:
        zone[1:] = (n-1)/n*(np.array(zone[1:])) + 1/n*np.array(data.loc[zone[0]])
        zones.updateRow(zone)
    del zone
    del zones
