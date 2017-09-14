from __future__ import division
import pandas as pd
from dbf2df import *
import arcpy

n = 5 #Averaging iteration number. Must be > 1. Average is ((n-1)/n)*df1 + 1/n*df2

#Define files
#dbf1 = r'P:\MPO\40 RTP and Air Quality\2045 LRTP\08_LandUseModel_Forecasting\Land Use Model Runs\BaseYearIncome\Initial2025Run2H\FILES\TAZ_OUT.DBF'
dbf1 = r'P:\MPO\40 RTP and Air Quality\2045 LRTP\08_LandUseModel_Forecasting\Land Use Model Runs\BY2015\FY2045Iter3\FILES\TAZ_OUT.DBF'
dbf2 = dbf1.replace('Iter3', 'Iter4')
out_dbf = dbf2.replace('.DBF', '_AVERAGED.DBF')

def dbf2df(dbf_file, index_col = 0):
    '''
    Reads the contents of a dbf file into a Pandas data frame
    '''
    columns = [field.name for field in arcpy.ListFields(dbf_file)][1:]
    df = pd.DataFrame(columns = columns)
    rows = arcpy.da.SearchCursor(dbf_file, columns)
    i = 0
    for row in rows:
        df.loc[i] = row
        i += 1
    df.set_index(columns[index_col])
    return df

#Read in data
df1 = dbf2df(dbf1)
df2 = dbf2df(dbf2)

#Create new data frame based on second
df = df2.copy()

#Replace values of df with averages of df1 and df2
te = 0
for col in df.columns:
    try:
        try:
            df[col] = ((n-1)/n*df1[col] + 1/n*df2[col]).astype(float)

            #Change the column to an integer if it needs to be. This could probably be better written
            if (df[col].astype(int) - df[col]).sum() == 0:
                df[col] = df[col].astype(int)
            elif col not in ['AREA', 'F_AREA', 'WRKRS_PER_']:
                df[col] = df[col].round().astype(int)
        except TypeError:
            te += 1
            continue
    except KeyError:
        continue

print '{} Type Errors'.format(te)
df2dbf(df, out_dbf, False)
