
# coding: utf-8

# In[ ]:

get_ipython().magic('matplotlib nbagg')


# In[ ]:

fname = '/Users/klay6683/Dropbox/SternchenAndMe/UVIS_Enc_Occ_2016_03_11/HSP2016_03_11_11_48_26_000_UVIS_233EN_ICYEXO001_PIE'


# In[ ]:

fname2 = '/Users/klay6683/Dropbox/SternchenAndMe/UVIS_Enc_Occ_2016_03_11/HSP2016_03_11_11_52_49_000_UVIS_233EN_ICYEXO001_PIE'


# In[ ]:

from pyuvis.io import HSP


# In[ ]:

HSP.sensitivity.plot()


# In[ ]:

hsp1 = HSP(fname, freq='2ms')
hsp2 = HSP(fname2, freq='2ms')


# In[ ]:

hsp1.timestr


# In[ ]:

hsp2.timestr


# In[ ]:

hsp1


# In[ ]:

hsp1.fname


# In[ ]:

hsp2


# In[ ]:

hsp2.fname


# In[ ]:

hsp1.times


# In[ ]:

hsp2.times


# In[ ]:

hsp1.get_first_minutes(1).head()


# In[ ]:

hsp1.get_last_minutes(1).head()


# In[ ]:

resampled = hsp1.cleaned_data_copy


# In[ ]:

resampled = resampled.resample('1s').mean()


# In[ ]:

from pandas import datetools


# In[ ]:

resampled[resampled.index[-1]-datetools.Minute(1):].plot()


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


# In[ ]:



