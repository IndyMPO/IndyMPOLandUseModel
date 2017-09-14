'''
CILUM utility functions
'''
import os

def check_scenario_directory(scenario_dir):
    '''
    Checks a scenario directory to make sure that all of the necessary files are inside

    Parameters
    ----------
    scenario_dir (str):
        Path of the scenario directory

    Returns
    -------
    missing_files (list):
        List of filepaths of missing files
    '''
    necessary_files = [r'vs_template.ctl',
                       r'FILES\agent2naics.csv', #Matrix for converting number of jobs by agent type to number of jobs by NAICS code
                       r'FILES\ALLOCATIONS.dbf', #Shapefile showing how agents and supply are allocated along with modeled rents
                       r'FILES\ALLOCATIONS.prj',
                       r'FILES\ALLOCATIONS.sbn',
                       r'FILES\ALLOCATIONS.sbx',
                       r'FILES\ALLOCATIONS.shp',
                       r'FILES\ALLOCATIONS.shx',
                       r'FILES\TAZ_OUT.DBF', #Shapefile with the travel demand model inputs
                       r'FILES\TAZ_OUT.shp',
                       r'FILES\TAZ_OUT.shx',
                       r'FILES\WorkersPerHH.csv', #File for estimating the number of workers based on the number of households in each agent category
                       r'MODEL\IndyLUM_VS.app', #Application file
                       r'MODEL\01CTL00A.CTL', #Control data
                       r'MODEL\01LUM00A.TXT', #Context file
                       r'MODEL\01LUM00A.INI', #Parameters
                       r'MODEL\01LUM00A.DEC', #Definition of endogenous variables
                       r'MODEL\Inputs\MGROW.dbf', #Control totals
                       r'MODEL\Inputs\ACCATT.dbf', #Accessibility and attractiveness
                       r'MODEL\Inputs\SUBSIDIES.dbf', #Subsidies and taxes
                       r'MODEL\Inputs\COMPETITION.dbf', #Defines which agents can bid on which real estate types in each zone
                       r'MODEL\Inputs\RHO.dbf', #Defines which real estate types can be built in each zone
                       r'MODEL\Inputs\ZONES.dbf', #Zonal data
                       r'MODEL\Inputs\REST.dbf', #Real estate attributes
                       r'MODEL\Inputs\AGENTS.dbf', #Agent attributes
                       r'MODEL\Inputs\BIDF.DBF', #Bid function parameters
                       r'MODEL\Inputs\ZNAMES.dbf', #Zone names (maps Cube Land zone number to TransCAD zone number)
                       r'MODEL\Inputs\RESTDESC.dbf', #Real estate names
                       r'MODEL\Inputs\MARKETS.dbf', #Defines markets
                       r'MODEL\Inputs\AGENTDESC.dbf', #Agent descriptions
                       r'MODEL\Inputs\BIDADJUST.dbf', #Bid adjustment factors
                       r'MODEL\Inputs\RENTADJUST.dbf', #Rent adjustment factors
                       r'MODEL\Inputs\ADJ_COST.dbf', #Cost adjustment factors
                       r'MODEL\Inputs\RESTRLOC.dbf', #Location restrictions
                       r'MODEL\Inputs\RESTRSUPPLY.dbf', #Supply restrictions
                       r'MODEL\Inputs\COSTF.DBF', #Cost function parameters
                       r'MODEL\Inputs\RENTF.DBF', #Rent function parameters
                       r'MODEL\01LND00A.PRN', #Print file
                       r'MODEL\Outputs\LOCATIONS.dbf', #Allocated agent locations
                       r'MODEL\Outputs\RENT.dbf', #Modeled rents
                       r'MODEL\Outputs\ZONES_OUT.dbf', #Endogenous variables
                       r'MODEL\Outputs\BIDS.dbf', #Modeled bids
                       r'MODEL\Outputs\SUPPLY.dbf', #Allocated supply
                       ]

    missing_files = []
    for necessary_file in necessary_files:
        full_path = os.path.join(scenario_dir, necessary_file)
        if not os.path.isfile(full_path):
            missing_files += [full_path]

    return missing_files

def get_scenario_tree(scenario_dir):
    '''
    Returns all of the parent scenarios of a given scenario by checking if they have the scenario file

    Parameters
    ----------
    scenario_dir (str):
        Scenario directory

    Returns
    -------
    scenario_tree(str):
        Tree of scenarios
    '''
    scenario_tree = []
    
    complete = False
    while not complete:
        if 'scenario.txt' in os.listdir(scenario_dir):
            split = os.path.split(scenario_dir)
            scenario_tree += [split[1]]
            scenario_dir = split[0]
        else:
            complete = True
            
    scenario_tree.reverse()
    return scenario_tree
