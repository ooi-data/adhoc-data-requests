"""Shared helpers for reading RCA data from the ooi-data S3 zarr bucket."""
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
