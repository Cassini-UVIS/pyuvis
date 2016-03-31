import datetime as dt

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pvl
import xarray as xr
from pandas import datetools
from pathlib import Path
from .hsp_sensitivity import sens_df


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


class UVIS_NetCDF(object):

    def __init__(self, fname, freq):
        self.path = Path(fname)
        self.fname = str(self.path)
        self.ds = xr.open_dataset(self.fname)
        self.freq = freq
        self.timestr = self.ds.start_time_str[:21] + '000'

    @property
    def start_time(self):
        timestr = self.timestr
        fmt = '%Y-%j %H:%M:%S.%f'
        return dt.datetime.strptime(timestr, fmt)

    @property
    def times(self):
        return pd.date_range(self.start_time, periods=self.n_integrations,
                             freq=self.freq)

    @property
    def n_integrations(self):
        return self.ds['integrations'].size


class HSP(UVIS_NetCDF):

    """Class for reading NetCDF UVIS HSP data files.

    Parameters
    ==========
    fname: {str, pathlib.Path}
        Path to file to read
    freq: str
        String indicating the sampling frequency, e.g. '1ms', '2ms'

    Examples
    ========
    hsp = hsp('path', '1ms')

    """
    sensitivity = sens_df

    def __init__(self, fname, freq):
        super().__init__(fname, freq)

    @property
    def n_integrations(self):
        return self.ds.counts.size

    @property
    def times(self):
        """HSP times are different in that one needs to stack all rows."""
        return pd.date_range(self.start_time, periods=self.n_integrations,
                             freq=self.freq)

    @property
    def series(self):
        s = pd.Series(self.ds.counts.values.ravel())
        s.index = self.times
        return s

    @property
    def counts_per_sec(self):
        ind = self.series.index
        td = ind[1] - ind[0]
        return self.series / td.total_seconds()

    def get_last_minutes(self, min):
        ind = self.series.index
        return self.series[ind[-1] - datetools.Minute(min):]

    def get_first_minutes(self, min):
        ind = self.series.index
        return self.series[:ind[0] + datetools.Minute(min)]

    @property
    def resampled(self):
        return self.counts_per_sec.resample('1s')

    @property
    def cleaned_data_copy(self):
        """Filtering out 0.5, 99.5 % outliers."""
        data = self.counts_per_sec.copy()
        min, max = np.percentile(data, (0.5, 99.5))
        data[data < min] = np.nan
        data[data > max] = np.nan
        return data

    def plot_resampled_with_errors(self, binning='1s', ax=None):
        data = self.cleaned_data_copy
        resampled = data.resample(binning)
        mean = resampled.mean()
        std = resampled.std()
        if ax is None:
            fig, ax = plt.subplots()
        mean.plot(yerr=std, ax=ax)
        ax.set_xlabel('Time')
        ax.set_ylabel('Counts per second')
        ax.set_title("Resampled to 1 s")

    def plot_relative_std(self, binning='1s', ax=None):
        data = self.cleaned_data_copy
        resampled = data.resample(binning)
        mean = resampled.mean()
        std = resampled.std()
        if ax is None:
            fig, ax = plt.subplots()
        (std / mean).plot(ax=ax)
        ax.set_xlabel("Time")
        ax.set_ylabel("Relative error per resample bin.")
        ax.set_title("Ratio of STD over mean value of resample bin.")

    def save_as_csv(self):
        to_save = self.resampled.mean()
        tdindex = to_save.index - to_save.index[0]
        to_save.index = tdindex.seconds
        to_save.to_csv(str(self.fname.with_suffix('.csv')))

    def __repr__(self):
        return self.ds.__repr__()


class FUV(UVIS_NetCDF):
    """FUV NetCDF reader class.

    Parameters
    ==========
    fname: {str, pathlib.Path}
        Path to file to read
    freq: str
        String indicating the sampling frequency, e.g. '1s', '2s'

    Examples
    ========
    fuv = FUV('path', '1s')
    """
    waves = np.linspace(111.5, 190, 512)

    def __init__(self, fname, freq):
        super().__init__(fname, freq)
        self.ds['integrations'] = self.times
        self.ds['spectral_dim_0'] = self.waves

    @property
    def data(self):
        return self.ds.window_0

    def __repr__(self):
        return self.ds.__repr__()
