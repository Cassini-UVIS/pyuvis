
# coding: utf-8

# In[1]:

fname = '/Users/klay6683/Dropbox/SternchenAndMe/UVIS_Enc_Occ_2016_03_11/HSP2016_03_11_11_48_26_000_UVIS_233EN_ICYEXO001_PIE'


# In[2]:

fname2 = '/Users/klay6683/Dropbox/SternchenAndMe/UVIS_Enc_Occ_2016_03_11/HSP2016_03_11_11_52_49_000_UVIS_233EN_ICYEXO001_PIE'


# In[29]:

import xarray as xr
import pandas as pd
import datetime as dt

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


# In[41]:

hsp = HSP(fname)


# In[42]:

hsp.timestr


# In[44]:

get_ipython().magic('matplotlib nbagg')


# In[45]:

hsp.series.resample('1s').mean().plot()

