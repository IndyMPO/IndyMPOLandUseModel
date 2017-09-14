#from dbf2df import *
import pandas as pd
import numpy as np
from tkFileDialog import *
from Tkinter import *
import arcpy

def normalize(array):
    '''
    Divides an array by its maximum value. Any negative values are replaced with zero
    '''
    array = array.astype(float)
    array[array < 0] = 0
    return array / array.max()

def dbf2df(dbf_file, index_col = 0):
    '''
    Places the entries of a dbf file into a Pandas data frame
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

#Tk().withdraw()

def main(src_file, zones_file):

    #Define fields in both input and output
    in_fields = ['ACC_POP', 'ACC_RET', 'ACC_NRE', 'ATT_POP', 'ATT_RET', 'ATT_NRE', 'TRN_ACC']
    out_fields = list(in_fields)
    for i in range(len(out_fields)):
        out_fields[i] += '_PK'
    out_fields[-1] = 'TRNACC_EMP'

    #Define files. Comment out Tkinter functions for interactivity
    #src_file = askopenfilename(title = 'Select a Source Table', defaultextension = 'dbf', filetypes = [('DBF file', '.dbf')])
    #zones_file = askopenfilename(title = 'Select a Scenario Zonal Table', defaultextension = 'dbf', filetypes = [('DBF file', '.dbf')])
    #zone_name_file = askopenfilename(title = 'Select a Zone Name Table', defaultextension = 'dbf', filetypes = [('DBF file', '.dbf')])
    #src_file = r'P:\MPO\40 RTP and Air Quality\2045 LRTP\08_LandUseModel_Forecasting\Land Use Model Runs\BaseYearIncome\Initial2025Run3M\FILES\TAZ_OUT.DBF'
    #zones_file = r'P:\MPO\40 RTP and Air Quality\2045 LRTP\08_LandUseModel_Forecasting\Land Use Model Runs\BaseYearIncome\Initial2025Run3M\MODEL\Inputs\ZONES.dbf'
    zone_name_file = zones_file.replace('ZONES', 'ZNAMES')
    #zones_file = r'C:\IndyLUM\Model\Mapping\ZONES2.dbf'

    #Read in data to memory
    src = dbf2df(src_file).set_index('TAZ')
    names = dbf2df(zone_name_file).set_index('IDZONE')['DESCZONE'].to_dict()

    #Normalize each field in the source data
    for field in in_fields:
        src[field] = normalize(src[field])

    #Update all of the values in the zones file
    zones = arcpy.da.UpdateCursor(zones_file, ['IDZONE'] + out_fields)
    for zone in zones:
        taz = names[zone[0]]
        for i in range(len(out_fields)):
            zone[i+1] = src.loc[taz, in_fields[i]]
        zones.updateRow(zone)
    del zone
    del zones

if __name__ == '__main__':

    src_file = r'P:\MPO\40 RTP and Air Quality\2045 LRTP\08_LandUseModel_Forecasting\Land Use Model Runs\BY2015\FY2045Iter1\FILES\TAZ_OUT.DBF'
    zones_file = r'P:\MPO\40 RTP and Air Quality\2045 LRTP\08_LandUseModel_Forecasting\Land Use Model Runs\BY2015\FY2045Iter1\MODEL\Inputs\ZONES.dbf'

    main(src_file, zones_file)
