
# coding: utf-8

# In[ ]:

get_ipython().magic('matplotlib nbagg')


# In[ ]:

fname = '/Users/klay6683/Dropbox/SternchenAndMe/UVIS_Enc_Occ_2016_03_11/HSP2016_03_11_11_48_26_000_UVIS_233EN_ICYEXO001_PIE'


# In[ ]:

from pyuvis.io import HSP
from pandas import datetools


# In[ ]:

hsp = HSP(fname, freq='2ms')


# In[ ]:

hsp


# In[ ]:

resampled = hsp.cleaned_data_copy


# In[ ]:

resampled = resampled.resample('1s').mean()


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

pix1 = fuv.data[:, 1].sum('spectral_dim_0')


# In[ ]:

hspdata = hsp.cleaned_data_copy


# In[ ]:

fuvdata = pix1.to_series()
low = np.percentile(fuvdata, 0.5)
fuvdata[fuvdata< low] = np.nan


# In[ ]:

fuvdata = fuvdata/fuvdata[10:75].mean()

fuvt0 = fuvdata.index[10]
fuvt1 = fuvdata.index[74]

t0_I0 = '2016-03-11 11:51:25'
t1_I0 = '2016-03-11 11:52:00'
I0 = hspdata[t0_I0:t1_I0].mean()

hspdata = hspdata / I0


# In[ ]:

df = pd.DataFrame(hspdata, columns=['hsp'])
df['fuv'] = fuvdata
subdf = df[df.index[-1] - datetools.Second(50):]


# In[ ]:

corrs = []
shifts = range(900, 1100, 2)
for i in shifts:
    resampled = subdf.hsp.shift(i, freq='ms').resample('1s').mean()
    corrs.append(resampled.corr(subdf.fuv))    

plt.figure()
plt.plot(shifts, corrs)

print(shifts[np.argmax(corrs)])


# In[ ]:

shifts = [990, 996, 1000]
fig, axes = plt.subplots(nrows=3)
for i,shift in enumerate(shifts):
    df = pd.DataFrame(hspdata.shift(shift,freq='ms'), columns=['hsp'])
    df['fuv'] = fuvdata
    subdf = df[df.index[-1] - datetools.Second(50):]
    subdf.resample('1s').mean().plot(ax=axes[i])


# In[ ]:

df = pd.DataFrame(hspdata.shift(990,freq='ms'), columns=['hsp'])

df['fuv'] = fuvdata

subdf = df[df.index[-1] - datetools.Second(50):]

subdf.resample('1s').mean().plot()


# In[ ]:

t0 = '2016-03-11 11:51:50'


# In[ ]:

fig, ax = plt.subplots()
resampled=df.resample('1s').mean()
resampled.hsp.plot(ax=ax, label='HSP', legend=True, lw=1.5)
resampled.fuv.plot(ax=ax, label='FUV', legend=True, lw=1.5)
plt.axvspan(t0_I0, t1_I0, facecolor='b', alpha=0.2)
plt.text(t0_I0, 0.92, r'$I_0(HSP)$', fontsize=16)
plt.axvspan(fuvt0, fuvt1, facecolor='g', alpha=0.2)
plt.text(fuvt0, 0.91, r'$I_0(FUV)$', fontsize=16)
ax.set_ylabel(r"$I/I_0$", fontsize=16)
ax.set_xlabel('Time', fontsize=16)
ax.set_title(r"Normalized, HSP vs FUV, showing $I_0$ regions")
plt.savefig("HSP_FUV_all_data_HSP990ms_shifted.pdf")


# In[ ]:

from matplotlib import dates


# In[ ]:

fig, ax = plt.subplots()
toplot = resampled.hsp[t0:]
toplot2 = resampled.fuv[t0:]
ax.plot_date(toplot.index, toplot, 'o-', label='HSP', markersize=3, lw=1.5)
ax.plot_date(toplot2.index, toplot2, 'v-', label='FUV', markersize=3,lw=1.5)
ax.xaxis.set_major_locator(dates.SecondLocator(interval=5))
ax.xaxis.set_major_formatter(dates.DateFormatter('%S'))
ax.grid()
ax.set_ylabel(r'$I / I_0$', fontsize=16)
ax.set_xlabel("Time [s]", fontsize=16)
ax.set_title("Last 50 s, normalized")
ax.legend()
fig.savefig("HSP_FUV_comparison_last_50s_HSP990ms_shifted.pdf")


# In[ ]:

fuv.data


# In[ ]:

fuv.data.coords


# In[ ]:

fuv.data.attrs


# In[ ]:

fuv.data.dims


# In[ ]:

data = fuv.data


# In[ ]:

fuv.times


# In[ ]:

hsp.times


# In[ ]:

hsp.n_integrations


# In[ ]:

hsp


# In[ ]:

fuv.data


# In[ ]:

fuv.data.sel(integrations=0).mean()


# In[ ]:

plt.figure()
fuv.data.mean(['spatial_dim_0', 'spectral_dim_0']).plot()


# In[ ]:

spec = fuv.data[100]


# In[ ]:

get_ipython().magic('matplotlib inline')


# In[ ]:

p = Path('./plots')


# In[ ]:

waves = np.linspace(111.5, 190, 512)


# In[ ]:

import xarray as xr


# In[ ]:

xrwaves = xr.DataArray(waves, dims=['wavelength'])


# In[ ]:

fuv.data.coords


# In[ ]:

fuv.data.dims


# In[ ]:

xr.DataArray(fuv.data, coords=[fuv.data.integrations,
                               fuv.data.spatial_dim_0,
                               fuv.data.spectral_dim_0])


# In[ ]:

fuv.data.coords


# In[ ]:

fuv.data.dims


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



