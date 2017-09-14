from dbf2df import *
import numpy as np
import sys
import os
import sys

tiny = np.finfo(float).tiny #Smallest floating point number (2**-1022). This is used to prevent divide by zero errors without changing nonzero values

def normalize(array):
    '''
    Divides an array by its maximum
    '''
    return array / array.max()

#Define files
#lumsdir = os.environ['CILUM']
lumsdir = sys.argv[1]
allocation_file = os.path.join(lumsdir, r'FILES\ALLOCATIONS.dbf')
agent_file = allocation_file.replace(r'FILES\ALLOCATIONS', r'MODEL\Inputs\AGENTS')
zones_file = agent_file.replace('AGENTS', 'ZONES')
znames_file = zones_file.replace('ZONES', 'ZNAMES')
out_file = allocation_file.replace('ALLOCATIONS.dbf', 'EndogVarOut.csv')

#Read in input files to memory
allocations = dbf2df(allocation_file).set_index('TAZ')
agents = dbf2df(agent_file)
res = agents.iloc[:10]
nres = agents.iloc[10:]
zones = dbf2df(zones_file)
znames = dbf2df(znames_file)

#Separate housholds and 1000 sq ft of nonresidential space from allocations data
hh = allocations[['A%d'%(a) for a in range(1, 11)]]
ksf = allocations[['A%d'%(a) for a in range(11, 19)]]
houses = allocations[['RE1', 'RE2', 'RE3']].sum(1)

#Create data frame for converting information between TransCAD and Cube zone numbers
taz2zone = znames.set_index('DESCZONE')
taz2zone['AREA'] = taz2zone['IDZONE'].map(zones.set_index('IDZONE')['LAND_AREA'])

#Create data frame for endogenous variables, and fill it with data
endogvar = pd.DataFrame(index = hh.index)
endogvar['PCTLOWINC'] = np.dot(hh.values, res['LOWINC']) / (hh.sum(1) + tiny)
endogvar['PBB_WHITE'] = np.dot(hh.values, res['WHITE']) / (hh.sum(1) + tiny)
endogvar['HOUSE_DEN'] = normalize(houses / (taz2zone['AREA'] + tiny))
endogvar['AVGHHINC'] = normalize(np.dot(hh.values, res['INCOME']) / (hh.sum(1) + tiny))
endogvar['EMPLOYMENT'] = normalize(np.dot(ksf.values, nres['KSFPERJOB']))

#Convert index from TransCAD zone number to Cube zone number
endogvar = endogvar.reset_index()
endogvar['IDZONE'] = endogvar['TAZ'].map(taz2zone['IDZONE'])
endogvar = endogvar.set_index('IDZONE')
del endogvar['TAZ']

#Write data to file
endogvar.to_csv(out_file)
