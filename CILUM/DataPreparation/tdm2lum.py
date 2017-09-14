from UpdateRunAccessibility import main as ura
from SetEndogVar import main as sev
from CreateScenario import main as cs
from CombineTransit import main as ct
import os
import arcpy

iteration = 4

skim_dir = r'I:\000JFLOOD\Cube Land\Data\2045 Forecasts\2045 LU4 Skims'
scenario_location = r'P:\MPO\40 RTP and Air Quality\2045 LRTP\08_LandUseModel_Forecasting\Land Use Model Runs\BY2015'
scenario = 'FY2045Iter4'
previous = 'FY2045Iter3'

tbx_file = r'P:\MPO\20_Data\IndyGeoTools\IndyGeoTools.tbx'
arcpy.ImportToolbox(tbx_file, 'IndyGeoTools')

scenario_dir = os.path.join(scenario_location, scenario)
previous_dir = os.path.join(scenario_location, previous)

auto_skim = os.path.join(skim_dir, 'Highway.csv')
transit_skim = os.path.join(skim_dir, 'Transit.csv')

zone_file = os.path.join(scenario_dir, r'MODEL\Inputs\ZONES.dbf')
taz_file = os.path.join(scenario_dir, r'FILES\TAZ_OUT.dbf')
endogvar_file = os.path.join(previous_dir, r'FILES\EndogVarOut.csv')

#Main script
#After skim csv creation
print 'Combining Transit Skims in {}\n'.format(skim_dir)
ct(skim_dir)

print 'Creating scenario {0} from {1} in {2}\n'.format(scenario, previous, scenario_location)
cs(scenario_location, scenario, previous)

print 'Calculating Accesibility\nAuto Skim: {0}\nTransit Skim: {1}\nTAZ File{2}\n'.format(auto_skim, transit_skim, taz_file)
arcpy.AccessibilityCalculator_IndyGeoTools(auto_skim, transit_skim, 20, 60, taz_file, 'TAZ', 'POP', 'EMPL', 'NCS44_45')

print 'Updating accessibility in {0} with values from {1}\n'.format(zone_file, taz_file)
ura(taz_file, zone_file)

print 'Updating endogenous variables in {0} with values from {1}\n'.format(zone_file, endogvar_file)
sev(endogvar_file, zone_file, iteration)

print 'Ready to run model!'
#Run model
#Average output
#Run summary
