cd C:\Python27\ArcGIS10.1
python C:\LandUseModel\tools\cilum\Scripts\runLand.py "J:\September Cube Land Skims\2016 Roads 2045 TAZ\Base\Iteration4\vs_template.ctl" temp "J:\September Cube Land Skims\2016 Roads 2045 TAZ\Base\Iteration4\MODEL"
python C:\LandUseModel\tools\cilum\Scripts\MapResults.py "J:\September Cube Land Skims\2016 Roads 2045 TAZ\Base\Iteration4"
python C:\LandUseModel\tools\cilum\Scripts\lu2tdm.py "J:\September Cube Land Skims\2016 Roads 2045 TAZ\Base\Iteration4"
python C:\LandUseModel\tools\cilum\Scripts\WriteSummary.py "J:\September Cube Land Skims\2016 Roads 2045 TAZ\Base\Iteration4"
python C:\LandUseModel\tools\cilum\Scripts\UpdateEndogVar.py "J:\September Cube Land Skims\2016 Roads 2045 TAZ\Base\Iteration4"