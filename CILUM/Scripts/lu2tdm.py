from __future__ import division
import arcpy
import numpy as np
from dbf2df import *
import os
import time
import sys

print 'Creating Travel Demand Model Inputs'

time_start = time.time()

lumsdir = os.environ['CILUM'].replace('/', '\\')

### READ IN FILES ###

allocation_file = os.path.join(lumsdir, r'FILES\ALLOCATIONS.dbf')
agent_file = os.path.join(lumsdir, r'MODEL\Inputs\AGENTS.dbf')
agent2naics_file = os.path.join(lumsdir, r'FILES\agent2naics.csv')
WorkersPerHH_file = os.path.join(lumsdir, r'FILES\WorkersPerHH.csv')
shapefile = os.path.join(lumsdir, r'FILES\TAZ_OUT.shp')
taz_out_file = os.path.join(lumsdir, r'FILES\TAZ_OUT.csv')

allocations = dbf2df(allocation_file).set_index('TAZ')
agents = dbf2df(agent_file)
agent2naics = pd.DataFrame.from_csv(agent2naics_file)
WorkersPerHH = pd.DataFrame.from_csv(WorkersPerHH_file)['WRKRSPERHH'].values

### DEFINE LISTS TO BE USED IN INDEXING ###

res_agents = ['A%d'%a for a in range(1, 11)]
nres_agents = ['A%d'%a for a in range(11, 19)]
naics_fields = ['NCS22', 'NCS23', 'NCS31_33', 'NCS42', 'NCS44_45', 'NCS48_49', 'NCS51', 'NCS52', 'NCS53',
                'NCS54', 'NCS55', 'NCS56', 'NCS61', 'NCS62', 'NCS71', 'NCS72', 'NCS81', 'NCS92']
taz_fields = ['POP', 'HH', 'EMPL', 'AVGINC'] + naics_fields + ['WRKRS_PER_']
static_fields = ['NCS11', 'NCS21', 'NCS99'] #Fields that won't be updated but are needed for calculations

### TRANSFORM LUM OUTPUTS TO TDM INPUTS ###

taz = pd.DataFrame(index = allocations.index, columns = taz_fields)

taz['HH'] = allocations[res_agents].sum(1)
taz['POP'] = np.dot(allocations[res_agents], agents['PERSONS'][:10])
taz['EMPL'] = np.dot(allocations[nres_agents], np.power(agents['KSFPERJOB'][10:], -1)).astype(float)
#taz['AVGINC'] = 1.376405343*np.dot(allocations[res_agents], agents['INCOME'][:10]) / taz['HH'].replace(0, np.inf)
taz['AVGINC'] = np.dot(allocations[res_agents], agents['INCOME'][:10]) / taz['HH'].replace(0, np.inf)

T = np.dot(np.diag(np.power(agents['KSFPERJOB'][10:], -1)), agent2naics.values) #Matrix for transforming built KSF by agent type to jobs by NAICS code
taz[naics_fields] = np.dot(allocations[nres_agents].values, T)

taz['WRKRS_PER_'] = np.dot(allocations[res_agents], np.hstack((WorkersPerHH, WorkersPerHH))) / (taz['HH'] + np.finfo(float).tiny)

### UPDATE EMPLOYMENT WITH STATIC VALUES ###

rows = arcpy.da.SearchCursor(shapefile, ['TAZ'] + static_fields)
for row in rows:
    taz.loc[row[0], 'EMPL'] += sum(row[1:])
del row
del rows

### UPDATE SHAPEFILE ###
rows = arcpy.da.UpdateCursor(shapefile, ['TAZ'] + taz_fields)
for row in rows:
    tazid = row[0]
    row[1:] = taz.loc[tazid]
    rows.updateRow(row)
del row
del rows

### WRITE NEW TDM INPUTS TO FILE ###

taz['WRKRSPERHH'] = taz['WRKRS_PER_']
taz.to_csv(taz_out_file)
del taz['WRKRS_PER_']

### END OF SCRIPT ###

runtime = round(time.time() - time_start, 1)
print 'Travel Demand Model inputs created in {} seconds'.format(runtime)
