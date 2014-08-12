# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>
from __future__ import print_function
from scipy.io import readsav
import pandas as pd
import numpy as np


def check_kernels(cell):
    if all(np.unique(cell) == np.array([''])):
        return np.NAN
    else:
        return cell


def swap_cell(cell):
    return cell.byteswap().newbyteorder()


def read_idlsav_file(file):
    tmp = readsav(file)
    # find largest substructure and return that
    key_of_longest = ''
    longestlength = 0
    print("Searching for longest substructure and returning that.")
    for thiskey in tmp.keys():
        thislength = len(tmp[thiskey])
        print("Found {} with length {}.".format(thiskey, thislength))
        if thislength > longestlength:
            key_of_longest = thiskey
            longestlength = thislength

    print("Return substructure with name {}.".format(key_of_longest))
    df = pd.DataFrame.from_records(tmp[key_of_longest])

    #print df.dtypes.values

    # There is a problem here. You see all these '>f8' datatypes in there?
    # This means that at least those parts of the IDL data structure is in the
    # inverse byte-ordering way than today's modern PC use, horrible!!
    # One needs to convert this, otherwise all the numbers can't be trusted.

    # print df.head()
    #print df.UVIS[0]

    # This looks like each cell has a 2D numpy array:
    # print df.UVIS[0].shape
    # print df.columns.values

    # Ok, let's change the columns that can be changed easily, i.e. the columns
    # that don't have arrays in each cell:
    df = df.apply(lambda x: x.values.byteswap().newbyteorder()
                  if x.dtype != 'O' else x)
    ## print df.dtypes.values

    # As you can see, the float dtypes are now pointing to the left ('<f8')
    # which means they are little-endian, as any normal computer is these days.
    # Now, let's put a proper index, `time` for instance:

    #df.index = pd.DatetimeIndex(df.UTC)
    ## print df.drop('UTC', axis=1, inplace=True)
    ## print df.index

    # Now, swap the bytes for each array in each DataFrame cell
    # first loop over columns, and then eeach column get's the lambda converter
    # func from above.

    for col in df.columns:
        if df[col].dtype != np.dtype('O'):
            try:
                df[col] = df[col].map(swap_cell)
            except TypeError:
                print(col, 'typeerror')
    #print df.UVIS.iloc[0].dtype
    #print df.dtypes.values

    # success!!
    # Now let's see if the KERNELS column actually ever has data:
    df.KERNELS = df.KERNELS.map(check_kernels)
    ## print 'wtf', df.KERNELS.notnull().value_counts()

    # This means that no KERNEL data was included, so we can drop it:
    # print df.drop('KERNELS', axis=1, inplace=True)
    # first only look at easy columns where there isn't an array per cell:
    # dtypecheck = df.dtypes != 'O'
    # easy_cols = dtypecheck[dtypecheck is True].index

    # note you can scroll the table to the right, but if it's wider or longer
    # than a certain number (settable) than it's truncated
    #print df[easy_cols]
    # Now it's your turn! ;)

    return df
