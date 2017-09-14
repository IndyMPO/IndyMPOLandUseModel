import arcpy
import pandas as pd
import numpy as np
import os
import sys
from dbfpy import dbf
from dbf2df import *
import pdb
#cwd = os.environ['CILUM']
#cwd = r'C:\CILUM\Base\BaseYearVS\Initial2025'
cwd = sys.argv[1]

data_file = os.path.join(cwd, 'MODEL\Outputs\SUPPLY.dbf')
location_file = os.path.join(cwd, 'MODEL\Outputs\LOCATIONS.dbf')
rent_file = os.path.join(cwd, 'MODEL\Outputs\RENT.dbf')
allocation_file = os.path.join(cwd, 'FILES\ALLOCATIONS.shp')
zone_map_file = os.path.join(cwd, 'MODEL\Inputs\ZNAMES.dbf')

def loadLocation( locPath ):
	#load Land outputs
#	land_data = randoms
	land_data = np.zeros((2550,18), dtype=np.float64)
	location_db = dbf.Dbf(locPath)
	for rec in location_db:
		i = rec["IDZONE"]
		h = rec["IDAGENT"]
		land_data[i-1,h-1] += rec["NLAGENT"]
	location_db.close()
	return land_data

##def dbf2df(dbf_file):
##    '''
##    Converts a dbf file into a Pandas data frame
##
##    Parameters
##    ----------
##    dbf_file (str):
##        Filepath of the dbf file
##
##    Returns
##    -------
##    df (pandas.DataFrame):
##        Data frame with the dbf file's data
##    '''
##    fields = [field.name for field in arcpy.ListFields(dbf_file)]
##    n_rows = int(arcpy.GetCount_management(dbf_file).getOutput(0))
##    n_cols = len(fields)
##    #df = pd.DataFrame(columns = fields)
##    data = np.empty((n_rows, n_cols), dtype = object)
##    rows = arcpy.da.SearchCursor(dbf_file, fields)
##    i = 0
##    for row in rows:
##        data[i, :] = row
##        i += 1
##
##    df = pd.DataFrame(data, columns = fields)
##    return df

print 'Reading dbfs'
data = dbf2df(data_file)
zone_map = dbf2df(zone_map_file).set_index('DESCZONE')['IDZONE'].to_dict()

print 'Reshaping supply'
#nrest = np.reshape(data['OCSUPPL'], (12, 2550)).T
#supply = pd.DataFrame(nrest, index = range(1, 2551), columns = range(1, 13))
supply = data.pivot(index = 'IDZONE', columns = 'IDREST', values = 'OCSUPPL')

print 'Reading locations'
locations = pd.DataFrame(loadLocation(location_file), index = range(1, 2551), columns = range(1, 19))

#pdb.set_trace()

print 'Reading rents'
rents = dbf2df(rent_file).reset_index().pivot(index = 'IDZONE', columns = 'IDREST', values = 'RENTS')

print 'Updating shapefiles'
zones = arcpy.da.UpdateCursor(allocation_file, ['TAZ'] + ['RE%d'%(i) for i in range(1, 13)] + ['A%d'%(i) for i in range(1, 19)] + ['R%d'%(i) for i in range(1, 13)])
for zone in zones:
    try:
            idzone = zone_map[zone[0]]
    except TypeError:
            pdb.set_trace()
    #zone[1:13] = supply.loc[idzone]
    #zone[13:31] = locations.loc[idzone]
    #zone[31:] = rents.loc[idzone]
    zone[1:43] = list(supply.loc[idzone]) + list(locations.loc[idzone]) + list(rents.loc[idzone])
    try:
            zones.updateRow(zone)
    except TypeError:
            pdb.set_trace()
del zone
del zones


