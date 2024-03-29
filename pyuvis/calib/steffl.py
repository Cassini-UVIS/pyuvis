# AUTOGENERATED! DO NOT EDIT! File to edit: notebooks/06_calib.steffl.ipynb (unless otherwise specified).

__all__ = ['steffl_spica_dates', 'steffl_spica_nasa_dates', 'Row2Row', 'create_detector_stack', 'Col2Col']

# Cell
from functools import cached_property

import matplotlib.pyplot as plt
import numpy as np
import param
from tqdm.auto import tqdm, trange

import holoviews as hv
import hvplot.xarray  # noqa
import pandas as pd
import xarray as xr
from nbverbose.showdoc import show_doc
from planetarypy.utils import iso_to_nasa_date
from .greg import filter_spica_for_date
from ..io import UVPDS, UVISObs
from ..pds import CatalogFilter

# Cell
steffl_spica_dates = ["2001-04-3", "2002-07-17", "2003-05-19"]
steffl_spica_nasa_dates = [iso_to_nasa_date(i) for i in steffl_spica_dates]
steffl_spica_nasa_dates

# Cell
class Row2Row:
    def __init__(self, pid):
        self.pid = pid
        self.data = UVPDS(pid).xarray.astype("int16")

    @property
    def plot_set(self):
        return self.data.hvplot.image(cmap="viridis", title=self.pid)

    @property
    def integrated(self):
        return self.data.sum(dim="samples")

    @property
    def plot_integrated(self):
        return self.integrated.hvplot(
            x="spectral", y="spatial", cmap="viridis", title=self.pid
        )

    @property
    def averaged(self):
        return self.integrated.sel(spatial=slice(3, 61)).mean(dim="spatial")

    @property
    def plot_averaged(self):
        return self.averaged.hvplot(title=self.pid)

    @property
    def column_std(self):
        return self.integrated.sel(spatial=slice(3, 61)).std(dim="spatial")

    @property
    def plot_column_std(self):
        return self.column_std.hvplot(title=f"{self.pid}, Column STD")

    @property
    def ff(self):
        data = self.averaged / self.integrated
        data = data.where(np.isfinite(data), other=np.nan)
        data.loc[:, 61:] = 1
        data.loc[:, :3] = 1
        return data

    @property
    def plot_ff(self):
        return self.ff.hvplot(cmap="viridis", title=self.pid, clim=(None, 4))

# Cell
def create_detector_stack(
    data,  # numpy 3D array to embed to xarray
    name,  # name of data
    third_dim,  # name of third dimension ("scan", "along", "across")
    orig,  # xarray to copy coords from
):
    """Function to create a 2D detector array with variable 3rd dimensions.

    It uses an `orig` array to copy the coordinates from.
    """
    return xr.DataArray(
        data,
        dims=["spectral", "spatial"] + [third_dim],
        coords={
            "spectral": orig.spectral,
            "spatial": orig.spatial,
            third_dim: range(data.shape[-1]),
        },
        name=name,
    )

# Cell
class Col2Col(param.Parameterized):
    pids = param.List(item_type=str, doc="List of product IDs")
    i = param.Integer(bounds=(0, 1023), doc="Spectral column i")
    m = param.Integer(bounds=(0, 13), doc="Scan number m")

    def __init__(
        self,
        pids,  # group of product ids for a raster run
        i=15,  # Minimum column value for evaluation (15:997)
        m=0,  # Default start scan
        plot_width=600,
    ):
        self.pids = pids
        self.i = i
        self.m = m
        self.plot_width = plot_width

    @cached_property
    def arr(self):
        scan_df = pd.DataFrame({"pids": sorted(self.pids)})
        scan_df.index.name = "m"

        stacked = []
        r2r_flats = []
        for m, pid in scan_df.iterrows():
            rowcorr = Row2Row(pid.get(0))
            stacked.append(rowcorr.integrated)
            r2r_flats.append(rowcorr.ff)

        self.stacked = np.dstack(stacked)
        self.r2r_flats = np.dstack(r2r_flats)

        arr = create_detector_stack(
            self.stacked, "Counts", "across_slit", rowcorr.integrated
        )
        self.r2r_flats = create_detector_stack(
            self.r2r_flats, "r2r flats", "across_slit", rowcorr.integrated
        )

        return arr

    def create_corrections_array(self):
        corr = xr.ones_like(self.arr.isel(scan=0, drop=True))
        corr = corr.expand_dims({"set": range(5)}, -1).copy()
        corr.name = "simple col2col corr"
        self.corrections = corr

    @property
    def r2r_flat_average(self):
        return self.r2r_flats.mean("across_slit")

    def r2r_flat_average_plot(self, **kwargs):
        return self.r2r_flat_average.hvplot.image(**self._get_opts(kwargs), **kwargs)

    @property
    def current_column_set(self):
        return [self.i, self.i + 4, self.i + 8]

    @property
    def current_scan_set(self):
        return [self.m, self.m + 5, self.m + 10]

    def plot(self):
        return self.arr.hvplot.image(
            cmap="viridis",
            clim=(1, 6000),
            widget_type="scrubber",
            widget_location="bottom",
            title="Across slit scan",
        )

    def plot_r2r_flats(self):
        return self.r2r_flats.hvplot.image(
            clim=(None, 2),
            cmap="viridis",
            widget_type="scrubber",
            widget_location="bottom",
            title="Row2Row flats for each across slit scan",
        )

    @param.depends("i", "m", watch=True)
    def get_column_data(self, arr=None):
        """Return triplet column data if available,else duplet for last raster scans.

        The watcher means, the result is cached unless i or m changes. (more performant)

        To get FF-corrected data, provide the FF-scaled data arr via `arr`.
        """
        if arr is None:
            arr = self.arr
        cols = []
        for col, scan in zip(self.current_column_set, self.current_scan_set):
            try:
                data = arr.isel(spectral=col, across_slit=scan, drop=True)
            except IndexError:
                break
            else:
                cols.append(data)
        result = xr.concat(cols, dim="set")
        result.name = "Column data counts"
        return result

    @property
    def averaged_columns(self):
        return self.get_column_data().mean("set")

    def plot_averaged_triplet(self):
        return self.averaged_columns.hvplot(label=f"{self.i=}, {self.m=}")

    def plot_triplet(self, i=None, corrected=False):
        if i is not None:
            self.i = i
        if corrected:
            cols = self.get_column_data(arr=self.corrected_arr)
        else:
            cols = self.get_column_data()
        plots = []
        for col, col_number in zip(cols, self.current_column_set):
            plots.append(col.hvplot(label=f"Columns {col_number}"))
        return hv.Overlay(plots)

    def calculate_simple_correction(self):
        # self.create_corrections_array()
        corrections = np.ones((1024, 64, 5), dtype="float")
        for m in trange(5, desc="Scan m", unit="scan"):
            self.m = m
            for i in range(1024):
                self.i = i
                # to calculate correction for column i, only use pixel values from i
                data = self.get_column_data()[0]
                # keep this in mind!
                data = data.where(data > 0, other=np.nan)
                corrections[i, :, m] = self.averaged_columns / data
        self.corrections = create_detector_stack(
            corrections, "simple flatfield", "set", self.arr
        )
        self.simple_correction = self.corrections.mean(axis=2)

    def _get_opts(self, kwargs):
        clim = kwargs.pop("clim", (None, 2))
        cmap = kwargs.pop("cmap", "viridis")
        width = kwargs.pop("width", self.plot_width)
        return {"clim": clim, "cmap": cmap, "width": width}

    def plot_Fm(self, m=0, **kwargs):
        return self.corrections.isel(set=m).hvplot(**self._get_opts(kwargs), **kwargs)

    def plot_all_Fm(self, **kwargs):
        plots = []
        for m in range(5):
            plots.append(self.plot_Fm(m, **kwargs))
        return hv.Layout(plots).cols(2)

    def plot_simple_correction(self, **kwargs):
        return self.simple_correction.hvplot(**self._get_opts(kwargs), **kwargs)

    @property
    def simple_both(self):
        ffc = self.r2r_flat_average * self.simple_correction
        # Normalization to unity at pixels [15:997, 3:60]
        inner_mean = ffc.isel(spectral=slice(15, 998), spatial=slice(3, 61)).mean()
        return ffc / inner_mean

    def simple_both_plot(self, **kwargs):
        return self.simple_both.hvplot(**self._get_opts(kwargs), **kwargs)

    @property
    def corrected_arr(self):
        arr = self.simple_both * self.arr
        arr.name = "FFC Counts"
        return arr