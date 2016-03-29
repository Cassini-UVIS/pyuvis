import numpy as np
from pathlib import Path
import pvl
import xarray as xr
import pandas as pd
import datetime as dt


class QUBE(object):

    def __init__(self, fname):
        self.path = Path(fname)
        # file management
        self.file_id = self.path.stem
        self.label_fname = self.path.with_suffix('.LBL')
        self.data_fname = self.path.with_suffix('.DAT')

        # read the data
        self.data1D = (np.fromfile(self.data_fname, '>H')).astype(np.uint16)

        # label stuff
        self.label = pvl.load(self.label_fname)
        self.cubelabel = self.label['QUBE']
        self.LINE_BIN = self.cubelabel['LINE_BIN']
        self.BAND_BIN = self.cubelabel['BAND_BIN']
        self.shape = tuple(self.cubelabel['CORE_ITEMS'])
        self.line_range = (self.cubelabel['UL_CORNER_LINE'],
                           self.cubelabel['LR_CORNER_LINE'])
        self.band_range = (self.cubelabel['UL_CORNER_BAND'],
                           self.cubelabel['LR_CORNER_BAND'])

        # reshape the data with infos from label
        self.data = self.data1D.reshape(self.shape, order='F')


class HSP(object):

    def __init__(self, fname, freq='1ms'):
        self.fname = fname
        self.ds = xr.open_dataset(fname)
        self.freq = freq
        self.timestr = self.ds.start_time_str[:21] + '000'

    @property
    def start_time(self):
        timestr = self.timestr
        fmt = '%Y-%j %H:%M:%S.%f'
        return dt.datetime.strptime(timestr, fmt)

    @property
    def series(self):
        s = pd.Series(self.ds.counts.values.ravel())
        s.index = pd.date_range(self.start_time, periods=len(s), freq=self.freq)
        return s

    def __repr__(self):
        return self.ds.__repr__()
