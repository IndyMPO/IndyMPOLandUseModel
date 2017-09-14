from dbfpy import dbf
import pandas as pd
import numpy as np
import time
import pdb

def dbf2df(filepath, index_col = None, conditions = None):
    '''
    Converts a dbf file to a pandas data frame

    Arguments:
        filepath (str): Filepath of dbf file
        index_col (str): Name of column to set as index
    '''

    ts = time.time()
    db = dbf.Dbf(filepath, True)

    header = db.fieldNames
    #df = pd.DataFrame(columns = header)
    data = np.empty((db.recordCount, len(header)), dtype = object)

    c = 0
    #pdb.set_trace()
    for _rec in db:
        #pdb.set_trace()
        row = _rec.asList()
        #print row
        #if conditions:
        #    record_row = True
        #    for condition in conditions:
        #        #print row[condition[0]], condition[1]
        #        if row[condition[0]] != condition[1]:
        #            record_row = False
        #else:
        #    record_row = True
        #print row, record_row
        #if record_row:
        data[c, :] = _rec.asList()
        c += 1
        #if c % 10000 == 0:
        #    print c
            
    df = pd.DataFrame(data, columns = header)
    if index_col:
        df = df.set_index(index_col)

    print 'Dbf file converted to data frame in ' + str(round(time.time() - ts, 1)) + ' seconds'
    return df

def get_dbf_fields(filepath):
    '''
    Returns list of field names in a dbf file

    Arguments:
        filepath (str): Filepath of dbf file

    Returns:
        fields (dict): Dict of field numbers and names
    '''
    
    db = dbf.Dbf(filepath, True)
    field_names = db.fieldNames
    fields = {}
    for i in range(len(field_names)):
        fields[i+1] = field_names[i]

    return fields

def df2dbf(df, filepath, include_index = True):
    '''
    Writes data frame to specified dbf file

    Arguments:
        df (Data Frame): Pandas data frame to convert to dbf
        filepath (str): Output filepath
    '''
    ts = time.time()
    db = dbf.Dbf(filepath, new = True)

    numeric_types = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    float_types = ['float16', 'float32', 'float64']
    int_types = ['int16', 'int32', 'int64']

    if include_index:
        try:
            df = df.reset_index()
        except ValueError:
            pass

    fields = df.columns.tolist()
    for col in fields:
        try:
            
            try:
                if type(df[col]) == pd.DataFrame:
                    continue
                if df[col].dtype in float_types:
                    db.addField((str(col), 'N', 16, 6))
                elif df[col].dtype in int_types:
                    db.addField((str(col), 'N', 16))
                else:
                    
                    db.addField((str(col), 'C', 255))
            except AttributeError:
                import pdb
                pdb.set_trace()
        except KeyError:
            print 'KeyError Happened'
            continue

    for record in df.index:
        rec = db.newRecord()
        for col in fields:
            if type(df[col]) == pd.DataFrame:
                continue
            try:
                rec[col] = df.loc[record, col]
                #print df.loc[record, col], rec[col]
            except ValueError:
                print 'ValueError Happened'
                continue
        rec.store()

    #pdb.set_trace()

    db.close()
    print 'Data frame converted to dbf in ' + str(round(time.time() - ts, 1)) + ' seconds'

def test_inverse():
    df = pd.DataFrame([[1, 2, 'Buckle My Shoe'],
                       [3, 4, 'Shut the Door'],
                       [5, 6, 'Pick Up Sticks'],
                       [7, 8, 'Lay them Straight'],
                       [9, 10, "I've heard variations on this one"]],
                      columns = ['N1', 'N2', 'Rhyme'])
    outfile = 'H:\Rhyme.dbf'
    df2dbf(df, outfile)
