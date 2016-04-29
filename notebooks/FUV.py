
# coding: utf-8

# # FUV

# In[1]:

from pathlib import Path
from pyuvis.io import FUV, HSP, UVIS_NetCDF


# In[2]:

folder = Path('/Users/klay6683/Dropbox/SternchenAndMe/UVIS_Enc_Occ_2016_03_11')


# In[3]:

fuvfiles = list(folder.glob('*FUV*'))


# In[4]:

fuvfiles[0]


# In[5]:

fuv = FUV(fuvfiles[0])


# In[6]:

fuv.data


# In[24]:

get_ipython().magic('matplotlib inline')


# In[25]:

import seaborn as sns
sns.set_context('notebook')


# In[26]:

fig, ax = plt.subplots(figsize=(8,6))
fuv.data[:,0].plot(ax=ax)
fig.tight_layout()


# In[28]:

fuv.data[:, 1, 100].plot()
plt.tight_layout()


# In[30]:

plt.figure()
fuv.data.mean(['spatial_dim_0', 'wavelengths']).plot()


# In[31]:

spec = fuv.data[100]


# In[32]:

spec


# In[34]:

p = Path('./plots')


# In[35]:

plt.figure()
fuv.data[0][1].plot()


# In[36]:

plt.figure()
fuv.data[:,1,100].plot()


# In[40]:

plt.figure()
fuv.data.sum(['wavelengths'])[:, 1].plot()


# In[ ]:



