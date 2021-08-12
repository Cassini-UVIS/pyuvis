# pyuvis
> This package provides tools to work with Cassini UVIS data.


## How to install

`pip install pyuvis`

## How to use

The tools in here depend on my now also much improved general `planetarypy` package, and the pip installer will look for the minimum required version of 0.12.

When launched for the first time, `planetarypy` will ask for a storage path for all data managed by `planetarypy`.

When using the `planetarypy.ctx` or `planetarypy.hirise` modules for the first time, they will automatically find, download, and convert the respective PDS index file, so please be patient.
After this it will be very fast, as the index is stored in HDF5 format.

If you are later interested in getting these indexes for more data search, do this:
