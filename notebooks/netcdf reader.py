
# coding: utf-8

# In[3]:

get_ipython().magic('matplotlib nbagg')


# In[4]:

fname = '/Users/klay6683/Dropbox/SternchenAndMe/UVIS_Enc_Occ_2016_03_11/HSP2016_03_11_11_48_26_000_UVIS_233EN_ICYEXO001_PIE'


# In[5]:

fname2 = '/Users/klay6683/Dropbox/SternchenAndMe/UVIS_Enc_Occ_2016_03_11/HSP2016_03_11_11_52_49_000_UVIS_233EN_ICYEXO001_PIE'


# In[35]:

import xarray as xr
import pandas as pd
import datetime as dt
from pandas import datetools

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
        return self.series[ind[-1] - datetools.Minute(min):]

    def get_first_minutes(self, min):
        ind = self.series.index
        return self.series[:ind[0] + datetools.Minute(min)]

    @property
    def cleaned_data_copy(self):
        """Filtering out 0.5, 99.5 % outliers."""
        data = self.counts_per_sec.copy()
        min,max = np.percentile(data, (0.5, 99.5))
        data[data < min]=np.nan
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
        
    def __repr__(self):
        return self.ds.__repr__()


# In[36]:

hsp = HSP(fname)


# In[37]:

hsp.timestr


# In[38]:

hsp.times


# In[39]:

hsp.get_first_minutes(1).head()


# In[40]:

hsp.get_last_minutes(1).head()


# In[41]:

hsp.plot_resampled_with_errors()


# In[42]:

hsp.plot_relative_std()


# In[27]:

hsp.series.tail()


# In[16]:

np.percentile(hsp.series, (0.5, 99.5))


# In[18]:

hsp.series.describe()


# In[ ]:



