# pyuvis


Python tools for Cassini UVIS data

See how the example notebook looks like:
http://nbviewer.ipython.org/gist/michaelaye/42948a8c7ffa1f0330e9

Dependencies:
* pandas
* xarray (for NetCDF files)


## INSTALL
```bash
git clone git@github.com:michaelaye/pyuvis.git
cd pyuvis

```
Then if you want to keep coding in it (engineering install):
```bash
pip install -e .
```
to make any changes immediately available to your Python environment.
Or:
```bash
pip install .
```
if you want a more stable install that only changes behaviour when you execute another install.


## QUBE reader

Basic usage:

```python
from pyuvis import QUBE
import matplotlib.pyplot as plt

fname = path_to_UVIS_file
qube = QUBE(fname)
print qube.shape # shortcut to qube.data.shape
# often the line range in the data is reduced and the previews are
# averages over the first axis (often) not always.
plt.imshow(qube.data.mean(axis=0)[qube.line_range[0],qube.line_range[1]]

```

The `fname` can either be to the `.LBL` or `.DAT` file, as long as both are next to each other in the same folder.

## SAV reader

basic usage:
```python
from pyuvis.readers import read_idlsav_file

data = read_idlsav_file(fname)
```
The reader determines which is the biggest structure inside the SAV file and return only that. Print-out for that search is provided.
Returned data file is a pandas.Dataframe.


## HSP reader

```python
from pyuvis.io import HSP

# default time delta is 1 ms, one can give other values here if known:
hsp = HSP(fname[, freq='1ms'])

# time has a real time object now, parsed from timestr
print(hsp.timestr, hsp.start_time)

# hsp.series is a pandas TimeSeries with correctly indexed times
print(hsp.series.head())

# resample and plot in one go:
hsp.series.resample('1s').mean().plot()
```
