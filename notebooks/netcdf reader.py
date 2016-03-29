
# coding: utf-8

# In[1]:

get_ipython().magic('matplotlib nbagg')


# In[2]:

fname = '/Users/klay6683/Dropbox/SternchenAndMe/UVIS_Enc_Occ_2016_03_11/HSP2016_03_11_11_48_26_000_UVIS_233EN_ICYEXO001_PIE'


# In[3]:

fname2 = '/Users/klay6683/Dropbox/SternchenAndMe/UVIS_Enc_Occ_2016_03_11/HSP2016_03_11_11_52_49_000_UVIS_233EN_ICYEXO001_PIE'


# In[62]:

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


# In[63]:

hsp = HSP(fname)


# In[64]:

hsp.timestr


# In[65]:

hsp.times


# In[66]:

hsp.get_first_minutes(1).head()


# In[67]:

hsp.get_last_minutes(1).head()


# In[68]:

hsp.plot_resampled_with_errors()


# In[47]:

resampled = hsp.counts_per_sec.resample('1s')


# In[37]:

mean = resampled.sum()


# In[38]:

std = resampled.std()


# In[39]:

plt.figure()
mean.plot()


# In[40]:

hsp.series.tail()


# In[19]:

plt.figure()
(std/mean).plot()


# In[ ]:



