# pyuvis


Python tools for Cassini UVIS data

See how the example notebook looks like:
http://nbviewer.ipython.org/gist/michaelaye/42948a8c7ffa1f0330e9

Dependencies:
* pypds (module: pds, PDS label reader)
* pandas

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
