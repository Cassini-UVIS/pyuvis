
# coding: utf-8

# In[1]:

get_ipython().magic('matplotlib nbagg')


# In[2]:

fname = '/Users/klay6683/Dropbox/SternchenAndMe/UVIS_Enc_Occ_2016_03_11/HSP2016_03_11_11_48_26_000_UVIS_233EN_ICYEXO001_PIE'


# In[3]:

fname2 = '/Users/klay6683/Dropbox/SternchenAndMe/UVIS_Enc_Occ_2016_03_11/HSP2016_03_11_11_52_49_000_UVIS_233EN_ICYEXO001_PIE'


# In[4]:

from pyuvis.io import HSP


# In[5]:

HSP.sensitivity.plot()


# In[6]:

hsp1 = HSP(fname, freq='2ms')
hsp2 = HSP(fname2, freq='2ms')


# In[7]:

hsp1.timestr


# In[8]:

hsp2.timestr


# In[9]:

hsp1


# In[10]:

hsp1.fname


# In[11]:

hsp2


# In[12]:

hsp2.fname


# In[13]:

hsp1.times


# In[14]:

hsp2.times


# In[15]:

hsp1.get_first_minutes(1).head()


# In[16]:

hsp1.get_last_minutes(1).head()


# In[17]:

resampled = hsp1.cleaned_data_copy


# In[18]:

resampled = resampled.resample('1s').mean()


# In[19]:

from pandas import datetools


# In[20]:

plt.figure()
resampled[resampled.index[-1]-datetools.Minute(1):].plot()


# In[25]:

plt.figure()
hsp1.counts_per_sec[::2].resample('1s').mean().plot(label='even', legend=True)
hsp1.counts_per_sec[1::2].resample('1s').mean().plot(label='uneven', legend=True)
hsp1.counts_per_sec.resample('1s').mean().plot(label='all', legend=True)


# In[ ]:

plt.figure()
hsp2.cleaned_data_copy.resample('1s').mean().plot()


# In[ ]:

last_minute = hsp1.get_last_minutes(1)


# In[ ]:

last_minute.resample('1s').mean().plot()


# In[ ]:

hsp1.plot_resampled_with_errors()


# In[ ]:




# In[ ]:

hsp.plot_relative_std()


# In[ ]:

hsp.series.tail()


# In[ ]:

np.percentile(hsp.series, (0.5, 99.5))


# In[ ]:

hsp.series.describe()


# # FUV

# In[26]:

from pathlib import Path


# In[27]:

folder = Path('/Users/klay6683/Dropbox/SternchenAndMe/UVIS_Enc_Occ_2016_03_11')


# In[37]:

fuvfiles = list(folder.glob('*FUV*'))


# In[53]:

import xarray as xr
import pandas as pd

class FUV(object):
    def __init__(self, fname):
        self.path = Path(fname)
        self.ds = xr.open_dataset(str(self.path))
        
    def __repr__(self):
        return self.ds.__repr__()


# In[54]:

fuvfiles[0]


# In[55]:

fuv = FUV(fuvfiles[0])


# In[56]:

fuv


# In[57]:

fuv.ds.dims


# In[60]:

fuv.ds.window_0


# In[67]:

fuv.ds.window_0


# In[ ]:

fuv.ds.window_0


# In[35]:

hsp1


# In[ ]:



