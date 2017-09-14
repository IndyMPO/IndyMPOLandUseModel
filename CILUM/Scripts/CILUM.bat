cd C:\Python27\ArcGIS10.1
python C:\CILUM\Scripts\runLand.py "J:\September Cube Land Skims\Cube Land Scenarios\2016 Roads 2045 TAZ\Base\Iteration2\vs_template.ctl" temp "J:\September Cube Land Skims\Cube Land Scenarios\2016 Roads 2045 TAZ\Base\Iteration2\MODEL"
python C:\CILUM\Scripts\MapResults.py
python C:\CILUM\Scripts\lu2tdm.py
python C:\CILUM\Scripts\WriteSummary.py
python C:\CILUM\Scripts\UpdateEndogVar.py
python C:\CILUM\Scripts\RunCompleted.py