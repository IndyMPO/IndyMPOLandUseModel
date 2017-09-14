from __future__ import division
import pandas as pd
import numpy as np
import os
from shutil import copy, copytree
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
    nrows = int(arcpy.GetCount_management(dbf_file).getOutput(0))
    ncols = len(columns)
    df = pd.DataFrame(np.zeros((nrows, ncols), dtype = object), columns = columns)
    rows = arcpy.da.SearchCursor(dbf_file, columns)
    i = 0
    for row in rows:
        df.loc[i] = row
        i += 1
    df.set_index(columns[index_col])
    return df

def AddSkimHeader(fp):
    '''
    Adds skim headers!
    '''
    skim = pd.DataFrame.from_csv(fp, header = None)
    skim.columns = skim.index
    skim.to_csv(fp)

def CombineTransitSkims(eb_file, lb_file, N):
    '''
    Combines transit skims!
    '''
    #Read in data, and fill null values with infinity
    eb = pd.DataFrame.from_csv(eb_file).fillna(np.inf)
    lb = pd.DataFrame.from_csv(lb_file).fillna(np.inf)

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
    transit.to_csv(lb_file.replace('LocalBus', 'Transit'))

def CreateNewScenario(scenario_name, year, description, base_scenario_directory, destination_scenario_directory = None, fixed_supply = False):
    '''
    Creates a new scenario!
    '''
    if destination_scenario_directory is None:
        destination_scenario_directory = base_scenario_directory

    try:
        os.rmdir(os.path.join(base_scenario_directory, 'MODEL', 'Inputs', 'Shapefiles'))
    except WindowsError:
        pass

    #Check for invalid scenario name 
    assert scenario_name not in ['MODEL', 'FILES'], 'New scenario name cannot be "MODEL" or "FILES"'

    #Check if scenario already exists
    new_scenario_directory = os.path.join(destination_scenario_directory, scenario_name)
    if os.path.isdir(new_scenario_directory):
        raise ValueError('Scenario {} already exists'.format(new_scenario_directory))

    #Create new scenario directory and copy files from the base scenario
    os.mkdir(new_scenario_directory)
    copytree(os.path.join(base_scenario_directory, 'FILES'), os.path.join(new_scenario_directory, 'FILES'))
    copytree(os.path.join(base_scenario_directory, 'MODEL'), os.path.join(new_scenario_directory, 'MODEL'))
    copy(os.path.join(base_scenario_directory, 'vs_template.ctl'), os.path.join(new_scenario_directory, 'vs_template.ctl'))

    #Write year and description files
    with open(os.path.join(new_scenario_directory, r'FILES\YEAR.txt'), 'w') as f:
        f.write(str(year))
        f.close()

    with open(os.path.join(new_scenario_directory, 'scenario.txt'), 'w') as f:
        f.write(description)
        f.close()

def CopyModelInputs(previous_scenario_directory, new_scenario_directory):
    '''
    Copies model inputs!
    '''
    try:
        os.rmdir(os.path.join(previous_scenario_directory, 'MODEL', 'Inputs', 'Shapefiles'))
    except WindowsError:
        pass
    
    for f in os.listdir(os.path.join(previous_scenario_directory, r'MODEL\Inputs')):
        copy(os.path.join(os.path.join(previous_scenario_directory, r'MODEL\Inputs'), f),
             os.path.join(os.path.join(new_scenario_directory, r'MODEL\Inputs'), f))

def UpdateRunAccessibility(scenario_directory):
    '''
    Updates run accessibility!
    '''
    src_file = os.path.join(scenario_directory, 'FILES', 'TAZ_OUT.dbf')
    zones_file = os.path.join(scenario_directory, 'MODEL', 'Inputs', 'ZONES.dbf')
    zone_name_file = zones_file.replace('ZONES', 'ZNAMES')

    #Define fields in both input and output
    in_fields = ['ACC_POP', 'ACC_RET', 'ACC_NRE', 'ATT_POP', 'ATT_RET', 'ATT_NRE', 'TRN_ACC']
    out_fields = list(in_fields)
    for i in range(len(out_fields)):
        out_fields[i] += '_PK'
    out_fields[-1] = 'TRNACC_EMP'
    
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

def SetEndogenousVariables(previous_scenario_directory, new_scenario_directory, iteration_number):
    '''
    Sets endogenous variables!
    '''
    n = iteration_number
    src_file = os.path.join(previous_scenario_directory, 'FILES', 'EndogVarOut.csv')
    zone_file = os.path.join(new_scenario_directory, 'MODEL', 'Inputs', 'ZONES.dbf')

    #Read in input data
    data = pd.DataFrame.from_csv(src_file, index_col = None).fillna(0)
    fields = data.columns.tolist()
    data = data.set_index('IDZONE')

    #Update zonal file with averaged values (or input values themselves if this is the first iteration)
    zones = arcpy.da.UpdateCursor(zone_file, fields)
    for zone in zones:
        if n == 1:
            zone[1:] = data.loc[zone[0]]
        else:
            zone[1:] = (n-1)/n*np.array(zone[1:]) + 1/n*np.array(data.loc[zone[0]])
        zones.updateRow(zone)
        
    del zone
    del zones
