
# coding: utf-8

# In[1]:

fname = ("/Users/klay6683/Dropbox/SternchenAndMe/UVIS_Enc_Occ_2016_03_11"
         "/HSP2016_03_11_11_48_26_000_UVIS_233EN_ICYEXO001_PIE")


# In[2]:

from pyuvis.io import HSP


# In[3]:

hsp = HSP(fname, freq='2ms')


# ### Resampling and summing vs Scaling and mean value
# 
# Just to follow our discussion and to show that things are making sense, I compare the 2 things that we agreed should be the same:
# 
# * Resampling the raw data into 1 second bins and sum them up, or
# * Scaling each raw sample to counts per second by multiplying with sampling frequency (which I do inside the `counts_per_sec` function), and then get the mean value of the 1 second resampling bin.
# 
# This works here in the way that the `resample` command actually creates an abstract resampler that can be re-used in multiple ways with different aggregation functions, to allow maximum flexibility.
# That's why I call the `sum()` or `mean()` function **AFTER** the `resample` call.

# In[4]:

hsp.series.resample('1s').sum().head()


# In[5]:

hsp.counts_per_sec.resample('1s').mean().head()


# .. with the counts per seconds looking like this:

# In[6]:

hsp.counts_per_sec.head()

