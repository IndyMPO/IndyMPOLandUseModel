from Scripts.util import check_scenario_directory
import os

def run(scenario_dir):

    #Check for missing files
    missing_files = check_scenario_directory(scenario_dir)
    if len(missing_files) > 0:
        raise IOError('Necessary file(s) missing:\n' + '\n'.join(missing_files))

    #Define batch file lines
    batch_lines = [r'cd C:\Python27\ArcGIS10.1',
                   r'python C:\LandUseModel\tools\cilum\Scripts\runLand.py "{0}\vs_template.ctl" temp "{0}\MODEL"'.format(scenario_dir), #Run model
                   r'python C:\LandUseModel\tools\cilum\Scripts\MapResults.py "{0}"'.format(scenario_dir), #Place supply and agents into result shapefile
                   r'python C:\LandUseModel\tools\cilum\Scripts\lu2tdm.py "{0}"'.format(scenario_dir), #Convert land use model outputs into travel demand model inputs
                   r'python C:\LandUseModel\tools\cilum\Scripts\WriteSummary.py "{0}"'.format(scenario_dir), #Writes an Excel summary of the results
                   r'python C:\LandUseModel\tools\cilum\Scripts\UpdateEndogVar.py "{0}"'.format(scenario_dir)] #Updates endogenous variables

    #Write batch file
    batch_file = r'C:\LandUseModel\tools\cilum\Scripts\CILUM.bat'
    with open(batch_file, 'w') as batch:
        batch.write('\n'.join(batch_lines))
        batch.close()

    #Execute batch file
    os.system(batch_file)
