import shutil
import os

def main(base, scenario, previous):

    scenario_dir = os.path.join(base, scenario)
    previous_dir = os.path.join(base, previous)

    print 'Copying base files into scenario files'
    os.mkdir(scenario_dir)
    shutil.copytree(os.path.join(base, 'FILES'), os.path.join(scenario_dir, 'FILES'))
    shutil.copytree(os.path.join(base, 'MODEL'), os.path.join(scenario_dir, 'MODEL'))
    shutil.copy(os.path.join(base, 'vs_template.ctl'), os.path.join(scenario_dir, 'vs_template.ctl'))

    #Remove old inputs
    input_dir = os.path.join(scenario_dir, r'MODEL\Inputs')
    for f in os.listdir(input_dir):
        os.remove(os.path.join(input_dir, f))
    os.rmdir(input_dir)

    print 'Copying previous iteration files'
    shutil.copytree(os.path.join(previous_dir, r'MODEL\Inputs'), input_dir)
    shutil.copy(os.path.join(previous_dir, r'FILES\YEAR.txt'), os.path.join(scenario_dir, r'FILES\YEAR.txt'))
    shutil.copy(os.path.join(previous_dir, r'FILES\TAZ_OUT.dbf'), os.path.join(scenario_dir, r'FILES\TAZ_OUT.dbf'))

    description = raw_input('Enter a scenario description:\n')
    with open(os.path.join(scenario_dir, 'scenario.txt'), 'w') as f:
        f.write(description)
        f.close()

if __name__ == '__main__':

    base = r'P:\MPO\40 RTP and Air Quality\2045 LRTP\08_LandUseModel_Forecasting\Land Use Model Runs\BaseYearIncome'
    prev = 'MagicSpreadsheet'
    new = 'TEST'

    main(base, new, prev)
