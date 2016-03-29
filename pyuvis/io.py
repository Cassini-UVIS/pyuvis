import datetime as dt

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pvl
import xarray as xr
from pandas.datetools import Minute
from pathlib import Path


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
    def times(self):
        return self.series.index

    @property
    def series(self):
        s = pd.Series(self.ds.counts.values.ravel())
        s.index = pd.date_range(self.start_time, periods=len(s), freq=self.freq)
        return s

    @property
    def counts_per_sec(self):
        ind = self.series.index
        td = ind[1]-ind[0]
        return self.series / td.total_seconds()

    def get_last_minutes(self, min):
        ind = self.series.index
        return self.series[ind[-1]-Minute(min):]

    def get_first_minutes(self, min):
        ind = self.series.index
        return self.series[:ind[0]+Minute(min)]

    def plot_resampled_with_errors(self, binning='1s', ax=None):
        resampled = self.counts_per_sec.resample('1s')
        mean = resampled.mean()
        std = resampled.std()
        if ax is None:
            fig, ax = plt.subplots()
        mean.plot(yerr=std, ax=ax)
        ax.set_xlabel('Time')
        ax.set_ylabel('Counts per second')
        ax.set_title("Resampled to 1 s")

    def __repr__(self):
        return self.ds.__repr__()
