import os
import time
from datetime import datetime

from tools import *
from config import *

print('===START: {}===\n'.format(datetime.now().strftime('%A %B %d, %Y %I:%M:%S %p')))

if run_step_2:
    print('Adding Skim Headers')
    start_time = time.time()
    dpt.AddSkimHeader(auto_skim_file)
    dpt.AddSkimHeader(local_bus_skim_file)
    if brt:
        dpt.AddSkimHeader(brt_skim_file)
    end_time = time.time()
    run_time = end_time - start_time
    print('Skim headers added in {} seconds'.format(round(run_time, 1)))

if run_step_3:
    if brt:
        print('Combining Transit Skims')
        start_time = time.time()
        dpt.CombineTransitSkims(brt_skim_file, local_bus_skim_file, 2550)
        end_time = time.time()
        run_time = end_time - start_time
        print('Transit skims combined in in {} seconds'.format(round(run_time, 1)))

if run_step_4:
    print('Creating New Scenario')
    start_time = time.time()
    dpt.CreateNewScenario(new_scenario_name, model_year, description, base_scenario_directory)
    end_time = time.time()
    run_time = end_time - start_time
    print('New scenario created in {} seconds'.format(round(run_time, 1)))


if run_step_5:
    print('Copying Model Inputs from Previous Iteration')
    start_time = time.time()
    dpt.CopyModelInputs(os.path.join(base_scenario_directory, previous_scenario_name), os.path.join(base_scenario_directory, new_scenario_name))
    end_time = time.time()
    run_time = end_time - start_time
    print('Model inputs from Previous Iteration copied in {} seconds'.format(round(run_time, 1)))

if run_step_6:
    print('Calculating Accessibilities and Attractivenesses')
    start_time = time.time()
    taz_file = os.path.join(base_scenario_directory, new_scenario_name, 'FILES', 'TAZ_OUT.shp')
    if brt:
        AccessibilityCalculator(auto_skim_file, transit_skim_file, 20, 60, taz_file, 'TAZ', 'POP', 'EMPL', 'NCS44_45')
    else:
        AccessibilityCalculator(auto_skim_file, local_bus_skim_file, 20, 60, taz_file, 'TAZ', 'POP', 'EMPL', 'NCS44_45')
    end_time = time.time()
    run_time = end_time - start_time
    print('Acc and Att calculated in {} seconds'.format(round(run_time, 1)))

if run_step_7:
    print('Updating Input Accessibilities/Attractivenesses')
    start_time = time.time()
    dpt.UpdateRunAccessibility(os.path.join(base_scenario_directory, new_scenario_name))
    end_time = time.time()
    run_time = end_time - start_time
    print('Acc and Att updated in {} seconds'.format(round(run_time, 1)))

if run_step_8:
    if iteration_number > 1:
        print('Updating Endogenous Variables')
        start_time = time.time()
        dpt.SetEndogenousVariables(previous_scenario_directory, new_scenario_directory, iteration_number)
        end_time = time.time()
        run_time = end_time - start_time
        print('Endogenous variables updated in {} seconds'.format(round(run_time, 1)))
