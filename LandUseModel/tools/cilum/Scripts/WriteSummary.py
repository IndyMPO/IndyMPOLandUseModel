from __future__ import division
import time
ts = time.time()

from dbf2df import *
import arcpy
import os
import sys
import xlsxwriter as xl
from collections import OrderedDict
import numpy as np
from util import get_scenario_tree

def dbf2df(dbf_file, index_col = 0):
    columns = [field.name for field in arcpy.ListFields(dbf_file)][1:]
    df = pd.DataFrame(columns = columns)
    rows = arcpy.da.SearchCursor(dbf_file, columns)
    i = 0
    for row in rows:
        df.loc[i] = row
        i += 1
    df.set_index(columns[index_col])
    return df

#lumsdir = os.environ['CILUM']
#lumsdir = r'C:\CILUM\Base\BaseYearVS\Initial2025'
#lumsdir = r'P:\MPO\40 RTP and Air Quality\2045 LRTP\08_LandUseModel_Forecasting\Land Use Model Runs\BaseYearIncome\Initial2025Run1H'
lumsdir = sys.argv[1]

MunTwp_file = r'C:\CILUM\Files\TAZMunTwp.xlsx'
twp_name_file = r'C:\CILUM\Files\twp_name.csv'
TazCounty_file = r'C:\CILUM\Files\TazCounty.csv'

#Files with county-by-county projections
ibrc_file = r'C:\CILUM\FILES\IBRC.xlsx'
wp_file = ibrc_file.replace('IBRC', 'WP')

ibrc = {}
ibrc['Population'] = pd.read_excel(ibrc_file, 'Population')
ibrc['Jobs'] = pd.read_excel(ibrc_file, 'Jobs')

wp = {}
wp['Population'] = pd.read_excel(wp_file, 'Population')
wp['Households'] = pd.read_excel(wp_file, 'Households')
wp['Jobs'] = pd.read_excel(wp_file, 'Jobs')

outfile = os.path.join(lumsdir, 'FILES\{}Summary.xlsx'.format(os.path.split(lumsdir)[1]))
wb = xl.Workbook(outfile) #Output file

print 'Writing {}'.format(outfile.replace('/', '\\'))

scenarios = get_scenario_tree(lumsdir)
n_scenarios = len(scenarios)

mun = pd.read_excel(MunTwp_file, 'Municipalities').T
twp = pd.read_excel(MunTwp_file, 'Townships').T
TazCounty = pd.DataFrame.from_csv(TazCounty_file, header = None)[1].to_dict()
twp_name = pd.DataFrame.from_csv(twp_name_file, None)[1].to_dict()
for t in twp_name.keys():
    twp_name[str(t)] = twp_name[t]

formats = {}
font = 'Cambria'
formats['header'] = wb.add_format({'align': 'center', 'bold': True, 'bottom': True, 'font_name': font})
formats['index'] = wb.add_format({'align': 'left', 'font_name': font, 'right': True})
formats['total_index'] = wb.add_format({'align': 'left', 'bold': True, 'font_name': font, 'right': True})
formats['number'] = wb.add_format({'align': 'right', 'num_format': '#,##0', 'font_name': font})
formats['total_number'] = wb.add_format({'align': 'right', 'bold': True, 'num_format': '#,##0', 'font_name': font})
formats['percent'] = wb.add_format({'align': 'right', 'num_format': '#0.00%', 'font_name': font})
formats['total_percent'] = wb.add_format({'align': 'right', 'bold': True, 'num_format': '#0.00%', 'font_name': font})
formats['warning1'] = wb.add_format({'bg_color': '#ffff7f'})
formats['warning2'] = wb.add_format({'bg_color': '#ff7f7f'})
formats['warning3'] = wb.add_format({'bg_color': '#ff0000', 'font_color': '#ffffff'})
formats['warning4'] = wb.add_format({'bg_color': '#3f0000', 'font_color': '#ffffff'})

def get_data(outputs, col, scenarios, compare, weight = None):
    '''
    Retrieves data for writing into Excel sheet

    Parameters
    ----------
    outputs (dict):
        Dictionary of outputs to add
    col (str):
        Column in outputs to retrieve

    Returns
    -------
    data (pandas.DataFrame)
        Data frame with data to write
    '''
    initial_index = ['Total'] + outputs[outputs.keys()[0]]['COUNTY'].value_counts().sort_index().index.tolist()

    data = pd.DataFrame(index = initial_index, columns = outputs.keys()) #Data frame to be written

    if weight is None:
        weight = 'weight'
        

    #For each scenario, read the column into the data frame to be written
    for i in range(len(scenarios)):

        if weight == 'weight':
            outputs[scenarios[i]]['weight'] = np.ones_like(outputs[scenarios[i]].index)

        if weight != 'weight':
            outputs[scenarios[i]]['Product'] = outputs[scenarios[i]][col]*outputs[scenarios[i]][weight]
            county_results = outputs[scenarios[i]][['COUNTY', 'Product']].groupby('COUNTY').sum()['Product']
            county_results.loc['Total'] = county_results.sum()

        else:
            county_results = outputs[scenarios[i]][['COUNTY', col]].groupby('COUNTY').sum()[col]
            county_results.loc['Total'] = county_results.sum()

        #geos = ['Total'] + data.index.tolist()[:-1]

        data.loc[initial_index, scenarios[i]] = county_results.loc[initial_index]

        data.loc[' '] = np.nan
        
        for m in mun.index:
            data.loc[m, scenarios[i]] = 0
        mun_pop = np.dot(mun.values, (outputs[scenarios[i]][col]*outputs[scenarios[i]][weight]).values)
        data.loc[mun.index, scenarios[i]] = mun_pop

        data.loc['  '] = np.nan

        for t in twp.index:
##            name = twp_name[t].split(', ')[0]
##            cnty = twp_name[t].split(', ')[1]
            data.loc[twp_name[t], scenarios[i]] = 0
        twp_pop = np.dot(twp.values, (outputs[scenarios[i]][col]*outputs[scenarios[i]][weight]).values)
        data.loc[pd.Series(twp.index).map(twp_name), scenarios[i]] = twp_pop

    return data

def add_data(book, outputs, col, name = None, weight = None):
    '''
    Adds data to the workbook. If the scenario is a child scenario, each sheet compares it with its parent.

    Parameters
    ----------
    book (xlsxwriter.Workbook):
        Workbook to add data to
    outputs (dict):
        Dictionary of outputs to add
    col (str):
        Column in outputs to add to the book
    name (str):
        Name of sheet. If none is specified than the name of the column will be the sheet.
    '''
    global formats
    global twp_name
    global mun
    global twp
    global ibrc
    global wp

    if not name:
        name = col

    scenarios = outputs.keys()
    compare = (len(scenarios) == 2) #Only do comparison if the length of scenarios is 2

    data = get_data(outputs, col, scenarios, compare, weight)
    if weight:
        den_data = get_data(outputs, weight, scenarios, compare)
        #import pdb
        #pdb.set_trace()
        data /= (den_data + np.finfo(float).tiny)

    if compare: #Add columns for comparing data
        data['Difference'] = data[scenarios[1]] - data[scenarios[0]]
        data['% Difference'] = (data['Difference']) / (data[scenarios[0]] + np.finfo(float).tiny)

        year1 = int(open(os.path.join(os.path.split(lumsdir)[0], r'FILES\YEAR.txt'), 'r').read())
        year2 = int(open(os.path.join(lumsdir, r'FILES\YEAR.txt'), 'r').read())
        time_span = year2 - year1

        if time_span != 0:
            data['Annual Growth Rate'] = np.power(data[scenarios[1]]/(data[scenarios[0]] + np.finfo(float).tiny), 1/time_span) - 1
            
    else:
        year = int(open(os.path.join(lumsdir, r'FILES\YEAR.txt'), 'r').read())

    data = data.fillna(0)

    sheet = book.add_worksheet(name)

    #Write headers
    for j in range(len(scenarios)):
        sheet.write_string(0, j+1, scenarios[j], formats['header'])
    if compare:
        sheet.write_string(0, 3, 'Difference', formats['header'])
        sheet.write_string(0, 4, '% Difference', formats['header'])
        sheet.write_string(0, 5, 'Annual Growth Rate', formats['header'])
        sheet.write_string(0, 6, 'Woods & Poole', formats['header'])
        sheet.write_string(0, 7, 'IBRC', formats['header'])
    else:
        sheet.write_string(0, j+2, 'Woods & Poole', formats['header'])
        sheet.write_string(0, j+3, 'IBRC', formats['header'])

    counties = data.index
    for i in range(len(counties)):
        #Write county labels and data
        if counties[i] == 'Total':
            sheet.write_string(i+1, 0, 'Total', formats['total_index'])
            for j in range(len(scenarios)):
                sheet.write_number(i+1, j+1, data[scenarios[j]]['Total'], formats['total_number'])
            if compare:
                sheet.write_number(i+1, 3, data['Difference']['Total'], formats['total_number'])
                try:
                    sheet.write_number(i+1, 4, data['% Difference']['Total'], formats['total_percent'])
                except TypeError:
                    continue
                if time_span != 0:
                    sheet.write_number(i+1, 5, data['Annual Growth Rate']['Total'], formats['total_percent'])
                    
                try:
                    sheet.write_number(i+1, 6, wp[name][year2]['Total'], formats['total_number'])
                except KeyError:
                    pass
                try:
                    sheet.write_number(i+1, 7, ibrc[name][year2]['Total'], formats['total_number'])
                except KeyError:
                    pass
                
            else:
                try:
                    sheet.write_number(i+1, j+2, wp[name][year]['Total'], formats['total_number'])
                except KeyError:
                    pass
                try:
                    sheet.write_number(i+1, j+3, ibrc[name][year]['Total'], formats['total_number'])
                except KeyError:
                    pass
                
        elif counties[i] in [' ', '  ']:
            sheet.write_string(i+1, 0, ' ', formats['index'])

        else:
            sheet.write_string(i+1, 0, counties[i], formats['index'])
            for j in range(len(scenarios)):
                sheet.write_number(i+1, j+1, data[scenarios[j]][counties[i]], formats['number'])
            if compare:
                sheet.write_number(i+1, 3, data['Difference'][counties[i]], formats['number'])
                try:
                    sheet.write_number(i+1, 4, data['% Difference'][counties[i]], formats['percent'])
                except TypeError:
                    continue
                if time_span != 0:
                    sheet.write_number(i+1, 5, data['Annual Growth Rate'][counties[i]], formats['percent'])
                    
                try:
                    sheet.write_number(i+1, 6, wp[name][year2][counties[i]], formats['number'])
                except KeyError:
                    pass
                try:
                    sheet.write_number(i+1, 7, ibrc[name][year2][counties[i]], formats['number'])
                except KeyError:
                    pass
                
            else:
                try:
                    sheet.write_number(i+1, j+2, wp[name][year][counties[i]], formats['number'])
                except KeyError:
                    pass
                try:
                    sheet.write_number(i+1, j+3, ibrc[name][year][counties[i]], formats['number'])
                except KeyError:
                    pass

    #Set column widths
    sheet.set_column(0, 0, 20)
    if compare:
        sheet.set_column(1, 7, 20)
    else:
        sheet.set_column(1, len(scenarios) + 2, 20)

##    sheet.conditional_format('D3:D142', {'type': 'cell',
##                                         'criteria': 'between',
##                                         'minimum': -100000,
##                                         'maximum': -50000,
##                                         'format': formats['warning1']})
##    sheet.conditional_format('D3:D142', {'type': 'cell',
##                                         'criteria': 'between',
##                                         'minimum': -200000,
##                                         'maximum': -100000,
##                                         'format': formats['warning2']})
##    sheet.conditional_format('D3:D142', {'type': 'cell',
##                                         'criteria': 'between',
##                                         'minimum': -500000,
##                                         'maximum': -200000,
##                                         'format': formats['warning3']})
##    sheet.conditional_format('D3:D142', {'type': 'cell',
##                                         'criteria': '<=',
##                                         'value': -500000,
##                                         'format': formats['warning4']})
##    sheet.conditional_format('D3:D142', {'type': 'cell',
##                                         'criteria': 'between',
##                                         'minimum': 50000,
##                                         'maximum': 100000,
##                                         'format': formats['warning1']})
##    sheet.conditional_format('D3:D142', {'type': 'cell',
##                                         'criteria': 'between',
##                                         'minimum': 100000,
##                                         'maximum': 200000,
##                                         'format': formats['warning2']})
##    sheet.conditional_format('D3:D142', {'type': 'cell',
##                                         'criteria': 'between',
##                                         'minimum': 200000,
##                                         'maximum': 500000,
##                                         'format': formats['warning3']})
##    sheet.conditional_format('D3:D142', {'type': 'cell',
##                                         'criteria': '>=',
##                                         'value': 500000,
##                                         'format': formats['warning4']})

    if compare:

        sheet.conditional_format('E3:E142', {'type': 'cell',
                                             'criteria': 'between',
                                             'minimum': -1/2,
                                             'maximum': -1/3,
                                             'format': formats['warning1']})
        sheet.conditional_format('E3:E142', {'type': 'cell',
                                             'criteria': 'between',
                                             'minimum': -2/3,
                                             'maximum': -1/2,
                                             'format': formats['warning2']})
        sheet.conditional_format('E3:E142', {'type': 'cell',
                                             'criteria': 'between',
                                             'minimum': -5/6,
                                             'maximum': -2/3,
                                             'format': formats['warning3']})
        sheet.conditional_format('E3:E142', {'type': 'cell',
                                             'criteria': '<=',
                                             'value': -5/6,
                                             'format': formats['warning4']})
        sheet.conditional_format('E3:E142', {'type': 'cell',
                                             'criteria': 'between',
                                             'minimum': 1/2,
                                             'maximum': 1,
                                             'format': formats['warning1']})
        sheet.conditional_format('E3:E142', {'type': 'cell',
                                             'criteria': 'between',
                                             'minimum': 1,
                                             'maximum': 2,
                                             'format': formats['warning2']})
        sheet.conditional_format('E3:E142', {'type': 'cell',
                                             'criteria': 'between',
                                             'minimum': 2,
                                             'maximum': 5,
                                             'format': formats['warning3']})
        sheet.conditional_format('E3:E142', {'type': 'cell',
                                             'criteria': '>=',
                                             'value': 5,
                                             'format': formats['warning4']})

    
        if time_span != 0:
            sheet.conditional_format('F3:F142', {'type': 'cell',
                                                 'criteria': '<',
                                                 'value': 0,
                                                 'format': formats['warning2']})
            sheet.conditional_format('F3:F142', {'type': 'cell',
                                                 'criteria': '>=',
                                                 'value': 0.05,
                                                 'format': formats['warning1']})
    

    sheet.freeze_panes(2, 0)


outputs = OrderedDict()
for i in range(n_scenarios):
    dir_index = n_scenarios - i - 1
    if dir_index == 0:
        out_file = lumsdir + '\\FILES\\TAZ_OUT.dbf'
    else:
        out_file = '\\'.join(lumsdir.replace('/', '\\').split('\\')[:-dir_index]) + '\\FILES\\TAZ_OUT.dbf'
    out_df = dbf2df(out_file)
    out_df['COUNTY'] = out_df['TAZ'].map(TazCounty)
    outputs[scenarios[i]] = out_df

add_data(wb, outputs, 'POP', 'Population')
add_data(wb, outputs, 'HH', 'Households')
add_data(wb, outputs, 'EMPL', 'Jobs')
add_data(wb, outputs, 'AVGINC', 'Average Income (2015$)', 'HH')
add_data(wb, outputs, 'NCS22', 'Utilities Jobs')
add_data(wb, outputs, 'NCS23', 'Construction Jobs')
add_data(wb, outputs, 'NCS31_33', 'Manufacturing Jobs')
add_data(wb, outputs, 'NCS42', 'Wholesale Jobs')
add_data(wb, outputs, 'NCS44_45', 'Retail Jobs')
add_data(wb, outputs, 'NCS48_49', 'Transport-Warehousing Jobs')
add_data(wb, outputs, 'NCS51', 'Information Jobs')
add_data(wb, outputs, 'NCS52', 'Finance and Insurance Jobs')
add_data(wb, outputs, 'NCS53', 'Real Estate Jobs')
add_data(wb, outputs, 'NCS54', 'Pro-Science-Tech Jobs')
add_data(wb, outputs, 'NCS55', 'Management Jobs')
add_data(wb, outputs, 'NCS56', 'Admin Jobs')
add_data(wb, outputs, 'NCS61', 'Education Jobs')
add_data(wb, outputs, 'NCS62', 'Healthcare Jobs')
add_data(wb, outputs, 'NCS72', 'Accommodation-Food Service Jobs')
add_data(wb, outputs, 'NCS92', 'Government Jobs')


wb.close()

runtime = time.time() - ts
print 'Summary file written in {} seconds'.format(round(runtime, 1))
