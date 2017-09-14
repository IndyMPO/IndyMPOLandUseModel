import os
import time
from subprocess import Popen
from datetime import datetime

from tools import *
from config import *

if run_step_9:
    print('Running Cube Land Model')
    start = time.time()
    cilum.run(new_scenario_directory)
    end = time.time()
    run_time = end - start
    print('Cube Land Model run in {} seconds'.format(round(run_time, 1)))

if run_step_10:
    print('Averaging Outputs')
    start = time.time()
    dbf1 = os.path.join(previous_scenario_directory, 'FILES', 'TAZ_OUT.dbf')
    dbf2 = os.path.join(new_scenario_directory, 'FILES', 'TAZ_OUT.dbf')
    out_dbf = dbf2.replace('TAZ_OUT', 'TAZ_OUT_AVERAGED')
    ppt.AverageOutputs(dbf1, dbf2, out_dbf, iteration_number + 1)
    end = time.time()
    run_time = end - start
    print('Outputs averaged in {} seconds'.format(round(run_time, 1)))

if run_step_11:
    print('Renaming Files')
    start = time.time()
    ppt.RenameFiles(new_scenario_directory)
    end = time.time()
    run_time = end - start
    print('Files renamed in {} seconds'.format(round(run_time, 1)))

if run_step_12:
    print('Recreating summary based on averaged outputs')
    start = time.time()
    ppt.RecreateSummary(new_scenario_directory)
    end = time.time()
    run_time = end - start
    print('Summary recreated in {} seconds'.format(round(run_time, 1)))

if open_summary_file_when_complete:
    summary_file = os.path.join(new_scenario_directory, 'FILES', '{}Summary.xlsx'.format(new_scenario_name))
    Popen(summary_file, shell = True)

print('\n===FINISH: {}==='.format(datetime.now().strftime('%A %B %d, %Y %I:%M:%S %p')))
