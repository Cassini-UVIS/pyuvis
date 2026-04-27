__all__ = ['get_star_obs', 'get_spica_obs', 'filter_spica_for_date']

from fastcore.utils import Path

import pandas as pd
from planetarypy.datetime_format_converters import fromdoyformat
from ..pds import CatalogFilter
from ..io import UVISObs

def get_star_obs():
    "Read Greg's file into dataframe and add some meta-columns."
    star_list = Path(
        "/home/maye/Dropbox/Documents/projects/uvis_pdart/calib/stars_list.txt"
    )
    star_obs = pd.read_table(
        star_list, sep="\s\s+", index_col=False, engine="python"
    )  # engine kw to avoid warning

    star_obs["detector"] = star_obs.filename.str[:3]
    star_obs["filename_time"] = star_obs.filename.map(
        lambda x: fromdoyformat(
            x[3:20].replace("_", "-", 1).replace("_", "T", 1).replace("_", ":")
        ).isoformat()
    )
    star_obs.filename_time = pd.to_datetime(star_obs.filename_time)
    star_obs["date"] = pd.DatetimeIndex(star_obs.filename_time.dt.date)
    star_obs["product_id"] = star_obs['filename'].str[:17]
    return star_obs

def get_spica_obs():
    "Filter Greg's list for Spica (alp vir) obs."
    return get_star_obs().query("name=='alp vir'")

def filter_spica_for_date(date: str):  # date in shape of yyyy-mm-dd
    return get_spica_obs().query("date==@date")
