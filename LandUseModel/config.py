import os

#Change iteration number
iteration_number = 4

auto_skim_file = r'J:\September Cube Land Skims\2016 Roads 2045 TAZ\Fourth Run\HW.csv'
local_bus_skim_file = auto_skim_file.replace('HW', 'LocalBus')
brt_skim_file = auto_skim_file.replace('HW', 'BRT')
transit_skim_file = local_bus_skim_file.replace('LocalBus', 'Transit')

base_scenario_directory = r'J:\September Cube Land Skims\2016 Roads 2045 TAZ\Base'
new_scenario_name = 'Iteration4'
previous_scenario_name = 'Iteration3'
new_scenario_directory = os.path.join(base_scenario_directory, new_scenario_name)
previous_scenario_directory = os.path.join(base_scenario_directory, previous_scenario_name)

#Change the model year - demographic year, change the descrip
model_year = 2045
description = 'Iteration {} of integrated model run with 2045 demographics and 2016 network'.format(iteration_number)

brt = os.path.isfile(brt_skim_file) #Checks whether or not a BRT skim is present

#Switches for controlling which steps to run
run_step_2  = 1 #Adding skim headers
run_step_3  = 1 #Combining transit skims
run_step_4  = 1 #Create new scenario
run_step_5  = 1 #Copy inputs from previous iteration
run_step_6  = 1 #Calculate accessibilities/attractivenesses
run_step_7  = 1 #Update accessibilities/attractivenesses
run_step_8  = 1 #Update endogenous variables
run_step_9  = 1 #Run Cube Land
run_step_10 = 1 #Average results with those of previous iteration
run_step_11 = 1 #Rename files
run_step_12 = 1 #Recreate summary with averaged outputs
open_summary_file_when_complete = 1
