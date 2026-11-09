"""Axial Seamount BOTPT seafloor uplift and TRHPH vent fluid data, binned hourly,
written as CSV + netCDF with plots, an interactive explore.html, a starter
notebook and a README, then zipped.

    uv run python package.py
"""
import shutil
import subprocess
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import xarray as xr
from plotly.subplots import make_subplots

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.ooi import export, open_stream, subset  # noqa: E402

HERE = Path(__file__).parent
START, END = "2014-01-01", "2026-11-01"  # fixed end so the zip can be recreated
NAME = f"axial_botpt_trhph_hourly_{START[:4]}-{END[:7]}"
PKG = HERE / "output" / NAME
PSI_TO_DBAR = 0.689476
ERUPTION = "2015-04-24"

BOTPT = {
    "RS03CCAL-MJ03F-05-BOTPTA301": "central_caldera",
    "RS03ECAL-MJ03E-06-BOTPTA302": "eastern_caldera",
    "RS03INT2-MJ03D-06-BOTPTA303": "international_district",
    "RS03ASHS-MJ03B-09-BOTPTA304": "ashes",
}
TRHPH = {
    "RS03INT1-MJ03C-10-TRHPHA301": "international_district",
    "RS03INT1-MJ03C-09-TRHPHA302": "international_district",
}

ATTRS = {
    "uplift_m": ("m", "Detided seafloor height change since the first day of record, positive = up"),
    "spike_flag": ("1", "1 = hour is more than 0.2 m from its 49 h running median, likely a sensor artifact"),
    "seafloor_depth_m": ("m", "Detided seafloor depth, positive down"),
    "predicted_tide_m": ("m", "Predicted ocean tide that was removed (OOI BOTSFLU tide model)"),
    "pressure_dbar": ("dbar", "Bottom pressure, NOT detided"),
    "temperature_mean_degC": ("degC", "Hourly mean vent fluid temperature"),
    "temperature_min_degC": ("degC", "Hourly minimum vent fluid temperature"),
    "temperature_max_degC": ("degC", "Hourly maximum vent fluid temperature"),
    "chloride_mmol_kg": ("mmol kg-1", "Hourly mean vent fluid chloride, derived from resistivity and temperature"),
    "deployment": ("1", "OOI deployment number; the probe is re-placed in the vent at each new deployment"),
    "n_samples": ("1", "Number of raw samples in the hour; 0 = no data"),
}


def finish(out, refdes, stream):
    for v, (units, desc) in ATTRS.items():
        if v in out:
            out[v].attrs = {"units": units, "description": desc}
    out.attrs = {"source": f"s3://ooi-data/{stream}", "reference_designator": refdes, "binning": "1 hour"}
    return out


def botpt(refdes):
    stream = f"{refdes}-streamed-botpt_nano_sample_15sec"
    ds = subset(open_stream(stream), START, END, ["botsflu_meandepth", "botsflu_predtide", "botsflu_meanpres"])
    h = ds.resample(time="1h")
    m = xr.merge([h.mean(), h.count().botsflu_meandepth.rename("n_samples")]).compute()
    elev = m.botsflu_meandepth  # detided, negative depth: increases as the seafloor rises
    uplift = elev - elev.dropna("time")[:24].mean()
    # source data has multi-hour sensor artifacts; does not flag the 2015 eruption
    spike = abs(uplift - uplift.rolling(time=49, center=True, min_periods=12).median()) > 0.2
    out = xr.Dataset({
        "uplift_m": uplift,
        "spike_flag": spike.astype("int8"),
        "seafloor_depth_m": -elev,
        "predicted_tide_m": m.botsflu_predtide,
        "pressure_dbar": m.botsflu_meanpres * PSI_TO_DBAR,
        "n_samples": m.n_samples,
    })
    return finish(out, refdes, stream)


def trhph(refdes):
    stream = f"{refdes}-streamed-trhph_sample"
    ds = subset(open_stream(stream), START, END, ["vent_fluid_temperature", "vent_fluid_chloride_conc", "deployment"])
    # drop fill values (~-2.5e9, inf) and physically implausible readings
    t = ds.vent_fluid_temperature.where((ds.vent_fluid_temperature > -2) & (ds.vent_fluid_temperature < 400))
    cl = ds.vent_fluid_chloride_conc.where((ds.vent_fluid_chloride_conc > 0) & (ds.vent_fluid_chloride_conc < 1000))
    out = xr.Dataset({
        "temperature_mean_degC": t.resample(time="1h").mean(),
        "temperature_min_degC": t.resample(time="1h").min(),
        "temperature_max_degC": t.resample(time="1h").max(),
        "chloride_mmol_kg": cl.resample(time="1h").mean(),
        "deployment": ds.deployment.resample(time="1h").max(),
        "n_samples": t.resample(time="1h").count(),
    }).compute()
    return finish(out, refdes, stream)


def clean(ds, var):
    return ds[var].where(ds.spike_flag == 0) if "spike_flag" in ds else ds[var]


def deployment_changes(ds):
    if "deployment" not in ds:
        return []
    dep = ds.deployment.dropna("time")
    return dep.time.where(dep.diff("time") > 0, drop=True).values


def plot(data, var, path, title):
    fig, axs = plt.subplots(len(data), 1, figsize=(12, 2.5 * len(data)), sharex=True, layout="constrained")
    for ax, (label, ds) in zip(axs, data.items()):
        clean(ds, var).plot(ax=ax, lw=0.5)
        ax.set_ylabel(ds[var].attrs["units"])
        for t in deployment_changes(ds):
            ax.axvline(t, color="k", ls=":", lw=0.8)
        ax.set_title(label, fontsize=9)
        ax.set_xlabel("")
    fig.suptitle(title)
    fig.savefig(path, dpi=120)
    plt.close(fig)


def explore_html(data, path):
    """Self-contained interactive page: daily means, linked zoom across all panels."""
    rows = [(k, ds, "uplift_m") for k, ds in data["botpt"].items()]
    rows += [(k, ds, "temperature_mean_degC") for k, ds in data["trhph"].items()]
    fig = make_subplots(rows=len(rows), cols=1, shared_xaxes=True, vertical_spacing=0.03,
                        subplot_titles=[f"{k}: {v}" for k, _, v in rows])
    for i, (label, ds, var) in enumerate(rows, 1):
        daily = clean(ds, var).resample(time="1D").mean()
        fig.add_scatter(x=daily.time.values, y=daily.values.round(3), mode="lines", line_width=1,
                        name=label, showlegend=False, row=i, col=1)
        fig.update_yaxes(title_text=ds[var].attrs["units"], row=i, col=1)
        for t in deployment_changes(ds):
            fig.add_vline(x=str(t)[:19], line_dash="dot", line_width=1, line_color="gray", row=i, col=1)
    fig.add_vline(x=ERUPTION, line_color="red", line_width=1, opacity=0.6, row="all", col=1)
    fig.update_layout(height=230 * len(rows), template="plotly_white", hovermode="x unified",
                      title="Axial Seamount, daily means. Drag to zoom, double-click to reset. "
                            "Red = April 2015 eruption, gray dotted = new TRHPH deployment")
    fig.write_html(path, include_plotlyjs=True, div_id="explore")  # fixed div_id keeps output reproducible


if __name__ == "__main__":
    shutil.rmtree(PKG, ignore_errors=True)
    data = {}
    for group, func, sites in [("botpt", botpt, BOTPT), ("trhph", trhph, TRHPH)]:
        data[group] = {}
        for refdes, site in sites.items():
            print(f"{refdes} ...")
            ds = func(refdes)
            export(ds, PKG / group / f"{refdes}_{site}_hourly")
            data[group][f"{refdes} ({site})"] = ds

    (PKG / "plots").mkdir()
    plot(data["botpt"], "uplift_m", PKG / "plots" / "botpt_uplift.png", "Detided seafloor uplift (flagged spikes removed)")
    plot(data["trhph"], "temperature_mean_degC", PKG / "plots" / "trhph_temperature.png",
         "Vent fluid temperature, hourly mean (dotted lines = new deployment)")
    explore_html(data, PKG / "explore.html")
    shutil.copy(HERE / "explore.ipynb", PKG)

    commit = subprocess.run(["git", "describe", "--always", "--dirty"], cwd=HERE, capture_output=True, text=True).stdout.strip()
    readme = (HERE / "package_README.md").read_text()
    (PKG / "README.md").write_text(readme.format(start=START, end=END, commit=commit))
    print("wrote", shutil.make_archive(str(PKG), "zip", PKG.parent, PKG.name))
