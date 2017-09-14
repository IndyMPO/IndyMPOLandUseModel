Macro "Main"

  dir = 'I:\000JFLOOD\Cube Land\Data\2025 Forecasts\2025 LU1 Skims\'
  mtx_file = dir + 'HSKIMS_AM.mtx'
  mtx = OpenMatrix(mtx_file, 'True')
  mcs = CreateMatrixCurrency(mtx, 'AM_TIME', 'Rows', 'Columns', )
  ExportMatrix(mcs, rows, 'Rows', 'CSV', 'C:\CILUM\DataPreparation\Highway.csv')

endMacro