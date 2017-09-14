import pandas as pd
import arcpy

src_file = r'I:\000JFLOOD\Cube Land\Data\2045 Forecasts\PBBWHITE2045.xlsx'
dest_file = r'P:\MPO\40 RTP and Air Quality\2045 LRTP\08_LandUseModel_Forecasting\Land Use Model Runs\BY2015\FY2045Iter1\MODEL\Inputs\ZONES.dbf'
src_col = 'p2045'
dest_col = 'PBB_WHITE'

src = pd.read_excel(src_file, 'ZONES').set_index('IDZONE')
pbb_map = src[src_col].to_dict()

zones = arcpy.da.UpdateCursor(dest_file, ['IDZONE', dest_col])
for zone in zones:
    zone[1] = pbb_map[zone[0]]
    zones.updateRow(zone)

del zone
del zones
