
# coding: utf-8

# # FUV

# In[ ]:

from pathlib import Path
from pyuvis.io import FUV, HSP


# In[ ]:

folder = Path('/Users/klay6683/Dropbox/SternchenAndMe/UVIS_Enc_Occ_2016_03_11')


# In[ ]:

fuvfiles = list(folder.glob('*FUV*'))


# In[ ]:

fuvfiles[0]


# In[ ]:

fuv = FUV(fuvfiles[0])


# In[ ]:

get_ipython().magic('matplotlib nbagg')


# In[ ]:

fuv.data[:, 1, 100].plot()


# In[ ]:




# In[ ]:




# In[ ]:

fuv.ds['integrations'] = fuv.times


# In[ ]:

fuv.ds


# In[ ]:

fuv.ds.reset_coords().set_coords('times')


# In[ ]:

fuv.data.attrs


# In[ ]:

fuv.data.dims


# In[ ]:

data = fuv.data


# In[ ]:

fuv.ds


# In[ ]:

fuv.ds['times'] = fuv.times


# In[ ]:

fuv.ds.reset_coords()


# In[ ]:




# In[ ]:

newfuv = fuv.ds.drop('integrations')


# In[ ]:

get_ipython().magic('matplotlib nbagg')


# In[ ]:

newfuv


# In[ ]:




# In[ ]:

plt.figure()
fuv.data.mean(['spatial_dim_0', 'spectral_dim_0']).plot()


# In[ ]:

spec = fuv.data[100]


# In[ ]:

p = Path('./plots')


# In[ ]:

waves = np.linspace(111.5, 190, 512)


# In[ ]:

import xarray as xr


# In[ ]:

xrwaves = xr.DataArray(waves, dims=['wavelength'])


# In[ ]:

data.coords


# In[ ]:

data.dims


# In[ ]:

data['spectral_dim_0'] = xrwaves


# In[ ]:

data


# In[ ]:

plt.figure()
data[0][1].plot()


# In[ ]:

data['times'] = fuv.times


# In[ ]:

data


# In[ ]:

plt.figure()
data[:,1,100].plot()


# In[ ]:

data.coords


# In[ ]:

data.dims


# In[ ]:

data['integrations'] = fuv.times


# In[ ]:

data.coords


# In[ ]:




# In[ ]:

data = np.random.rand(4, 3)

locs = ['IA', 'IL', 'IN']

times = pd.date_range('2000-01-01', periods=4)

foo = xr.DataArray(data, coords=[times, locs], dims=['time', 'space'])

foo


# In[ ]:

foo.dims


# In[ ]:

foo.coords


# In[ ]:

xr.DataArray(fuv.data, coords=[fuv.data.integrations,
                               fuv.data.spatial_dim_0])


# In[ ]:




# In[ ]:




# In[ ]:

fuv.ds.update({'wind':xrwaves})


# In[ ]:

newz = xr.DataArray(np.random.randn(3), [('y', [10,20,30])])
newz


# In[ ]:

xr.concat([arr, newz], dim='x')


# In[ ]:

arr


# In[ ]:

newz


# In[ ]:




# In[ ]:

for i,spec in enumerate(fuv.data):
    print(i)
    fig, ax = plt.subplots()
    ax.plot(xrwaves, spec[1])
    ax.set_ylim((0,72))
    fig.savefig("plots/spec_{}.png".format(str(i).zfill(3)), dpi=150)
    plt.close(fig)


# In[ ]:

spec[1]


# In[ ]:

import xarray as xr


# In[ ]:

waves = xr.DataArray(waves, dims=['wavelength'])


# In[ ]:

fuv.data.spectral_dim_0 = waves


# In[ ]:

plt.figure()
fuv.data.sum(['spectral_dim_0'])[:, 1].plot()


# In[ ]:

spec.spectral_dim_0 = waves


# In[ ]:

waves


# In[ ]:

np.percentile(fuv.data, 1.5)


# In[ ]:

fuv.data[0].plot


# In[ ]:

plt.figure()
hsp.resampled.mean().plot()


# In[ ]:



