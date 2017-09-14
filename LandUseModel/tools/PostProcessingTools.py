from __future__ import division
import os
import arcpy
import pandas as pd
from subprocess import call
from dbf2df import df2dbf

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

def AverageOutputs(dbf1, dbf2, out_dbf, n):
    '''
    Averages Outputs
    '''
    #Read in data
    df1 = dbf2df(dbf1)
    df2 = dbf2df(dbf2)

    try:
        del df1['Shape']
    except KeyError:
        pass

    try:
        del df2['Shape']
    except KeyError:
        pass

    #Create new data frame based on second
    df = df2.copy()

    #Replace values of df with averages of df1 and df2
    te = 0
    ve = 0
    for col in df.columns:
        try:
            try:
                try:
                    df[col] = ((n-1)/n*df1[col] + 1/n*df2[col]).astype(float)
                    #Change the column to an integer if it needs to be. This could probably be better written
                    if (df[col].astype(int) - df[col]).sum() == 0:
                        df[col] = df[col].astype(int)
                    elif col != 'WRKRS_PER_':
                        df[col] = df[col].round().astype(int)
                except ValueError:
                    print('Value Error in {}'.format(col))
                    ve += 1
            except TypeError:
                te += 1
                continue
        except KeyError:
            continue

    print '{} Type Errors'.format(te)
    print '{} Value Errors'.format(ve)
    df2dbf(df, out_dbf, False)

    #Delete the shape column from the csv
    try:
        del df['Shape']
    except KeyError:
        pass

    df['WRKRSPERHH'] = df['WRKRS_PER_']
    del df['WRKRS_PER_']

    df.to_csv(dbf2.replace('.dbf', '.csv'))

def RenameFiles(scenario_directory):
    '''
    Renames files!
    '''
    os.rename(os.path.join(scenario_directory, 'FILES', '{}Summary.xlsx'.format(os.path.split(scenario_directory)[1])),
              os.path.join(scenario_directory, 'FILES', '{}Summary_RAW.xlsx'.format(os.path.split(scenario_directory)[1])))
    os.rename(os.path.join(scenario_directory, 'FILES', 'TAZ_OUT.dbf'), os.path.join(scenario_directory, 'FILES', 'TAZ_OUT_RAW.dbf'))
    os.rename(os.path.join(scenario_directory, 'FILES', 'TAZ_OUT_AVERAGED.dbf'), os.path.join(scenario_directory, 'FILES', 'TAZ_OUT.dbf'))

def RecreateSummary(scenario_directory):
    '''
    Recreates the summary file after averaging
    '''
    batch_lines = [r'cd C:\Python27\ArcGIS10.1',
                   r'python C:\LandUseModel\tools\cilum\Scripts\WriteSummary.py "{0}"'.format(scenario_directory)]

    batch_file = r'C:\LandUseModel\tools\RecreateSummary.bat'
    with open(batch_file, 'w') as f:
        f.write('\n'.join(batch_lines))
        f.close()
    
    call(batch_file)
