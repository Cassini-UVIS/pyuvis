
# coding: utf-8

# In[1]:

get_ipython().magic('matplotlib nbagg')


# In[2]:

fname = '/Users/klay6683/Dropbox/SternchenAndMe/UVIS_Enc_Occ_2016_03_11/HSP2016_03_11_11_48_26_000_UVIS_233EN_ICYEXO001_PIE'


# In[3]:

from pyuvis.io import HSP


# In[4]:

HSP.sensitivity.plot()


# In[6]:

hsp = HSP(fname, freq='2ms')


# In[7]:

hsp.timestr


# In[8]:

hsp


# In[9]:

hsp.fname


# In[10]:

hsp.times


# In[11]:

hsp.get_first_minutes(1).head()


# In[12]:

hsp.get_last_minutes(1).head()


# In[13]:

resampled = hsp.cleaned_data_copy


# In[14]:

resampled = resampled.resample('1s').mean()


# In[15]:

last_minute = hsp.get_last_minutes(1)


# In[16]:

last_minute.resample('1s').mean().plot()


# In[17]:

hsp.plot_resampled_with_errors()


# In[18]:

hsp.plot_relative_std()


# In[31]:

hsp.series.tail()


# In[19]:

np.percentile(hsp.series, (0.5, 99.5))


# In[20]:

hsp.series.describe()


# # FUV

# In[1]:

from pathlib import Path
from pyuvis.io import FUV, HSP


# In[2]:

folder = Path('/Users/klay6683/Dropbox/SternchenAndMe/UVIS_Enc_Occ_2016_03_11')


# In[3]:

fuvfiles = list(folder.glob('*FUV*'))


# In[4]:

fuvfiles[0]


# In[5]:

fuv = FUV(fuvfiles[0])


# In[6]:

fuv


# In[7]:

get_ipython().magic('matplotlib inline')


# In[20]:

fuv.data.sum(['wavelengths','pixels']).plot()


# In[8]:

fuv.save_spectrums()


# In[9]:

fuv.create_spec_time_sequence_movie()


# In[10]:

fuv.save_spectograms()


# In[11]:

fuv.create_spectogram_movie()


# In[19]:

fuv.data[23].sum('pixels').plot()


# In[20]:

fuv.data[23].sum('pixels').max()


# In[205]:

obj = fuv.data[:, 1].sum('wavelengths')


# In[206]:

fuvdata = obj.to_series()
low = np.percentile(fuvdata, 0.5)
fuvdata[fuvdata< low] = np.nan


# In[207]:

fuvdata = fuvdata/fuvdata[10:75].mean()


# In[208]:

fuvt0 = fuvdata.index[10]
fuvt1 = fuvdata.index[74]


# In[116]:

t0_I0 = '2016-03-11 11:51:25'
t1_I0 = '2016-03-11 11:52:00'
I0 = resampled[t0_I0:t1_I0].mean()


# In[57]:

resampled = resampled / I0


# In[63]:

t0 = '2016-03-11 11:51:50'


# In[152]:

fig, ax = plt.subplots()
resampled.plot(ax=ax, label='HSP', legend=True, lw=1.5)
fuvdata.plot(ax=ax, label='FUV', legend=True, lw=1.5)
plt.axvspan(t0_I0, t1_I0, facecolor='b', alpha=0.2)
plt.text(t0_I0, 0.92, r'$I_0(HSP)$', fontsize=16)
plt.axvspan(fuvt0, fuvt1, facecolor='g', alpha=0.2)
plt.text(fuvt0, 0.91, r'$I_0(FUV)$', fontsize=16)
ax.set_ylabel(r"$I/I_0$", fontsize=16)
ax.set_xlabel('Time', fontsize=16)
ax.set_title(r"Normalized, HSP vs FUV, showing $I_0$ regions")
plt.savefig("HSP_FUV_all_data.pdf")


# In[159]:

fig, ax = plt.subplots()
toplot = resampled[t0:].shift(0)
toplot2 = fuvdata[t0:]
ax.plot_date(toplot.index, toplot, 'o-', label='HSP', markersize=3)
ax.plot_date(toplot2.index, toplot2, 'v-', label='FUV', markersize=3)
ax.xaxis.set_major_locator(dates.SecondLocator(interval=5))
ax.xaxis.set_major_formatter(dates.DateFormatter('%S'))
ax.grid()
ax.set_ylabel(r'$I / I_0$', fontsize=16)
ax.set_xlabel("Time [s]", fontsize=16)
ax.set_title("Last 50 s, normalized")
ax.legend()
fig.savefig("HSP_FUV_comparison_last_50s.pdf")


# In[12]:

fuv.data


# In[13]:

fuv.data.coords


# In[14]:

fuv.data.attrs


# In[40]:

fuv.data.dims


# In[15]:

data = fuv.data


# In[16]:

fuv.times


# In[17]:

hsp.times


# In[44]:

hsp.n_integrations


# In[45]:

hsp


# In[209]:

fuv.data


# In[210]:

get_ipython().magic('matplotlib inline')


# In[211]:

plt.figure()
fuv.data.mean(['pixels', 'wavelengths']).plot()


# In[24]:

get_ipython().magic('matplotlib inline')


# In[183]:

class UpdateQuad(object):

    def __init__(self, ax, data):
        self.ax = ax
        self.data = data
        self.quad = data[0].plot(vmax=72)

    def init(self):
        print('update init')
        self.quad.set_array(np.asarray([]))
        return self.quad

    def __call__(self, i):
        # data at time i
        ti = self.data[i]
        self.ax.clear()
#         self.quad.set_array(ti.data.ravel())
#         return self.quad
        return ti.plot(ax=self.ax)


fig, ax = plt.subplots()
ud = UpdateQuad(ax, fuv.data)
anim = animation.FuncAnimation(fig, ud, init_func=ud.init,
                               frames=10, blit=False)
anim.save('spectrograms2.mp4')


# In[269]:

wavemeans = fuv.data.mean('wavelengths')


# In[280]:

wavemeans.pixels


# In[284]:

plt.figure(figsize=(10,8))
for pix in [0,2,3,4]:
    (wavemeans[:, pix]/wavemeans[:, 1]).plot(label='pix %i' %pix)
plt.legend()
plt.title("Pixel signal relative to pixel 1")


# In[294]:

data.max().values


# In[312]:

data += 1e-


# In[307]:

from matplotlib.colors import LogNorm
data = fuv.data[100]
norm = LogNorm(vmin=1e-5, vmax=47)
data.plot(norm=norm)


# In[ ]:



