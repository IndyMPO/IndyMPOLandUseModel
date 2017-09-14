import os
from shutil import copytree, copy
import time

name = 'TestInit'
year = 2045
description = 'Testing test initialization'
test_directory = os.path.join(r'J:\September Cube Land Skims', name)

fixed_supply = False

#Define directories to be used
if fixed_supply:
    source_scenario_directory = r'C:\CILUM\Base\BaseYearFS'
else:
    source_scenario_directory = r'C:\CILUM\Base\BaseYearVS'
base_scenario_directory = os.path.join(test_directory, 'Base')
iter0_scenario_directory = os.path.join(base_scenario_directory, 'Iteration0')

#Create base year scenario and copy files from source scenario into it
print('Creating Base Scenario')
start = time.time()

os.mkdir(base_scenario_directory)
copytree(os.path.join(source_scenario_directory, 'FILES'), os.path.join(base_scenario_directory, 'FILES'))
copytree(os.path.join(source_scenario_directory, 'MODEL'), os.path.join(base_scenario_directory, 'MODEL'))
copy(os.path.join(source_scenario_directory, 'vs_template.ctl'), os.path.join(base_scenario_directory, 'vs_template.ctl'))

with open(os.path.join(base_scenario_directory, 'FILES', 'YEAR.txt'), 'w') as f:
    f.write('2015')
    f.close()

with open(os.path.join(base_scenario_directory, 'scenario.txt'), 'w') as f:
    f.write(description)
    f.close()

end = time.time()
run_time = end - start
print('Base Scenario Created in {} seconds'.format(round(run_time, 1)))

#Create iteration0 scenario
print('Creating Iteration0 Scenario')
start = time.time()

os.mkdir(iter0_scenario_directory)
copytree(os.path.join(base_scenario_directory, 'FILES'), os.path.join(iter0_scenario_directory, 'FILES'))
copytree(os.path.join(base_scenario_directory, 'MODEL'), os.path.join(iter0_scenario_directory, 'MODEL'))
copy(os.path.join(base_scenario_directory, 'vs_template.ctl'), os.path.join(iter0_scenario_directory, 'vs_template.ctl'))

with open(os.path.join(iter0_scenario_directory, 'FILES', 'YEAR.txt'), 'w') as f:
    f.write(str(year))
    f.close()

with open(os.path.join(iter0_scenario_directory, 'scenario.txt'), 'w') as f:
    f.write('Iteration 0 of ' + description)
    f.close()

#Copy initial zone, real estate, control total, and TAZ files
if year in [2025, 2045]:
    init_file_directory = r'C:\CILUM\Files\Init\{}'.format(year)
    for f in os.listdir(init_file_directory):
        if 'TAZ_OUT' in f:
            copy(os.path.join(init_file_directory, f), os.path.join(iter0_scenario_directory, 'FILES', f))
        else:
            copy(os.path.join(init_file_directory, f), os.path.join(iter0_scenario_directory, 'MODEL', 'Inputs', f))

end = time.time()
run_time = end - start
print('Iteration 0 created in {} seconds'.format(round(run_time, 1)))
