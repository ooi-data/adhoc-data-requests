"""Shared helpers for reading RCA data from the ooi-data S3 zarr bucket."""
from pathlib import Path

import s3fs
import xarray as xr

BUCKET = "ooi-data"


def open_stream(stream: str) -> xr.Dataset:
    """Lazily open a stream zarr, e.g. 'RS03AXPS-PC03A-4A-CTDPFA303-streamed-ctdpf_optode_sample'."""
    fs = s3fs.S3FileSystem(anon=True)
    return xr.open_zarr(fs.get_mapper(f"{BUCKET}/{stream}"), consolidated=True)


def subset(ds: xr.Dataset, start: str, end: str, variables: list[str] | None = None) -> xr.Dataset:
    ds = ds.sel(time=slice(start, end))
    return ds[[v for v in variables if v in ds]] if variables else ds


def export(ds: xr.Dataset, path: Path):
    """Write ds as path.csv and path.nc."""
    path.parent.mkdir(parents=True, exist_ok=True)
    ds.to_dataframe().to_csv(path.with_suffix(".csv"), float_format="%.6g")
    ds.to_netcdf(path.with_suffix(".nc"))
