import numpy as np
import arcpy

def extract_skim_from_csv(csv_file):
    '''
    Reads in a skim with labels as a csv and returns a 2-dimensional numpy array and a dictionary mapping zone to array index

    Parameters
    ----------
    csv_file (str):
        Filepath of the csv to read in
    '''
    data = np.genfromtxt(csv_file, delimiter = ',', filling_values = np.inf) #Read in data
    zones = data[0, :]
    zone_map = {zones[i+1]: i for i in range(len(zones)-1)} #Create dictionary for mapping zones
    skim = data[1:, 1:] #Define actual skim data
    return skim, zone_map

def apply_auto_decay_function(skim, auto_time_threshold, auto_function_decay):
    '''
    Applies a decay function to each element of an auto skim matrix

    Parameters
    ----------
    skim (ndarray):
        Skim matrix

    Returns
    -------
    weight_skim (ndarray):
        A matrix of weights with the same shape as `skim`
    '''
    return np.exp(-0.5*np.power(skim/auto_time_threshold, auto_function_decay))

def apply_transit_decay_function(skim, transit_time_threshold, transit_function_decay):
    '''
    Applies a decay function to each element of an auto skim matrix

    Parameters
    ----------
    skim (ndarray):
        Skim matrix

    Returns
    -------
    weight_skim (ndarray):
        A matrix of weights with the same shape as `skim`
    '''
    return np.exp(-0.5*np.power(skim/transit_time_threshold, transit_function_decay))

def calc_auto_acc(weight_skim, zone_map, taz_file, taz_field, pop_field, emp_field, ret_field, accpop_name, accret_name, accnre_name):
    '''
    Calculates the number of people, retail, and non-retail jobs within a threshold of each zone. Accessibilities in the input shapefile are updated.

    Parameters
    ----------
    weight_skim (ndarray):
        Weight skim
    zone_map (dict):
        Dictionary mapping zone number to index in the skim
    taz_file (str):
        Filepath for a TAZ shapefile
    '''
    pop = np.empty_like(weight_skim, dtype = int)
    ret = np.empty_like(weight_skim, dtype = int)
    nre = np.empty_like(weight_skim, dtype = int)

    #For each zone, create ndarrays that represent the number of people, retail, and non-retail jobs that can be reached within a specific time
    zones = arcpy.da.SearchCursor(taz_file, field_names = [taz_field, pop_field, emp_field, ret_field])
    for zone in zones:
        pop[:, zone_map[zone[0]]] = zone[1]*weight_skim[:, zone_map[zone[0]]]
        ret[:, zone_map[zone[0]]] = zone[3]*weight_skim[:, zone_map[zone[0]]]
        nre[:, zone_map[zone[0]]] = (zone[2] - zone[3])*weight_skim[:, zone_map[zone[0]]]

    #Calculate the row sums to get the total number of people, retail, and non-retail jobs that can be reached within a specific time for each origin zone
    acc_pop = pop.sum(1)
    acc_ret = ret.sum(1)
    acc_nre = nre.sum(1)

    #Update the shapefile with the calculated accessibilities
    zones = arcpy.da.UpdateCursor(taz_file, field_names = [taz_field, accpop_name, accret_name, accnre_name])
    for zone in zones:
        zone[1] = acc_pop[zone_map[zone[0]]]
        zone[2] = acc_ret[zone_map[zone[0]]]
        zone[3] = acc_nre[zone_map[zone[0]]]
        zones.updateRow(zone)

    #Unlock the shapefile
    del zone
    del zones

def calc_auto_att(weight_skim, zone_map, taz_file, taz_field, pop_field, emp_field, ret_field, attpop_name, attret_name, attnre_name):
    '''
    Calculates the number of people, retail, and non-retail jobs that can reach each zone within a specific time. Attractivenesses in the input shapefile are updated.

    Parameters
    ----------
    weight_skim (ndarray):
        Weight skim
    zone_map (dict):
        Dictionary mapping zone number to index in the skim
    taz_file (str):
        Filepath for a TAZ shapefile
    '''
    pop = np.empty_like(weight_skim, dtype = int)
    ret = np.empty_like(weight_skim, dtype = int)
    nre = np.empty_like(weight_skim, dtype = int)

    #For each zone, create ndarrays that represent the number of people, retail, and non-retail jobs that can reach a zone within a specific time
    zones = arcpy.da.SearchCursor(taz_file, field_names = [taz_field, pop_field, emp_field, ret_field])
    for zone in zones:
        pop[zone_map[zone[0]], :] = zone[1]*weight_skim[zone_map[zone[0]], :]
        ret[zone_map[zone[0]], :] = zone[3]*weight_skim[zone_map[zone[0]], :]
        nre[zone_map[zone[0]], :] = (zone[2] - zone[3])*weight_skim[zone_map[zone[0]], :]

    #Calculate the column sums to get the total number of people, retail, and non-retail jobs that can reach each destination zone within a specific time
    att_pop = pop.sum(0)
    att_ret = ret.sum(0)
    att_nre = nre.sum(0)

    #Update the shapefile with the calculated attractivenesses
    zones = arcpy.da.UpdateCursor(taz_file, field_names = [taz_field, attpop_name, attret_name, attnre_name])
    for zone in zones:
        zone[1] = att_pop[zone_map[zone[0]]]
        zone[2] = att_ret[zone_map[zone[0]]]
        zone[3] = att_nre[zone_map[zone[0]]]
        zones.updateRow(zone)

    #Unlock the shapefile
    del zone
    del zones

def calc_transit_acc(weight_skim, zone_map, taz_file, taz_field, emp_field, trnacc_name):
    '''
    Calculates the number of jobs that can be accessed by transit within a specified time for each zone. Accessibilities in the input shapefile are updated.

    Parameters
    ----------
    weight_skim (ndarray):
        Weight skim
    zone_map (dict):
        Dictionary mapping zone number to index in the skim
    taz_file (str):
        Filepath for a TAZ shapefile
    '''
    emp = np.empty_like(weight_skim, dtype = int)

    #Calculate number of jobs that can be reached by each origin zone in each destination zone within a specific time
    zones = arcpy.da.SearchCursor(taz_file, field_names = [taz_field, emp_field])
    for zone in zones:
        emp[:, zone_map[zone[0]]] = zone[1]*weight_skim[:, zone_map[zone[0]]]

    #Calculate the row sums to get the total number of jobs that each origin zone can reach within a specific time
    trn_acc = emp.sum(1)

    #Update the shapefile with the calculated accessbilities
    zones = arcpy.da.UpdateCursor(taz_file, field_names = [taz_field, trnacc_name])
    for zone in zones:
        zone[1] = trn_acc[zone_map[zone[0]]]
        zones.updateRow(zone)

    #Unlock the shapefiles
    del zone
    del zones

def main(auto_skim_file, transit_skim_file, auto_time_threshold, transit_time_threshold,
         taz_file, taz_field, pop_field, emp_field, ret_field):

    auto_function_decay = np.inf
    transit_function_decay = np.inf

    accpop_name = 'ACC_POP'
    accret_name = 'ACC_RET'
    accnre_name = 'ACC_NRE'
    attpop_name = 'ATT_POP'
    attret_name = 'ATT_RET'
    attnre_name = 'ATT_NRE'
    trnacc_name = 'TRN_ACC'

    current_fields = [field.aliasName for field in arcpy.ListFields(taz_file)]
    new_fields = [accpop_name, accret_name, accnre_name, attpop_name, attret_name, attnre_name, trnacc_name]
    for field in new_fields:
        if field not in current_fields:
            try:
                arcpy.AddField_management(taz_file, field, 'LONG')
            except Exception:
                print("Adding a new field didn't work")
                continue

    (auto, auto_zones) = extract_skim_from_csv(auto_skim_file)
    auto_weight = apply_auto_decay_function(auto, auto_time_threshold, auto_function_decay)
    (transit, transit_zones) = extract_skim_from_csv(transit_skim_file)
    transit_weight = apply_transit_decay_function(transit, transit_time_threshold, transit_function_decay)
    calc_auto_acc(auto_weight, auto_zones, taz_file, taz_field, pop_field, emp_field, ret_field, accpop_name, accret_name, accnre_name)
    calc_auto_att(auto_weight, auto_zones, taz_file, taz_field, pop_field, emp_field, ret_field, attpop_name, attret_name, attnre_name)
    calc_transit_acc(transit_weight, transit_zones, taz_file, taz_field, emp_field, trnacc_name)
    
