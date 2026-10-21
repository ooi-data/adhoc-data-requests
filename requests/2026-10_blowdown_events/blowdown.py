"""Shallow profiler 200 m platform (PC) blowdown events: quick-look plots of CTD, O2, pH and ADCP, streamed from s3://ooi-data.

    python blowdown.py            # all events
    python blowdown.py axial_2026 # one event
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.ooi import open_stream, subset  # noqa: E402

OUT = Path(__file__).parent / "output"
AVG = "1h"

EVENTS = {
    "axial_2026": ("RS03AXPS", "PC03A", "2026-03-01", "2026-06-30"),
    "slope_base_2026": ("RS01SBPS", "PC01A", "2026-07-01", "2026-08-31"),
    "slope_base_2020": ("RS01SBPS", "PC01A", "2020-09-01", "2020-10-31"),
    "slope_base_2019": ("RS01SBPS", "PC01A", "2019-05-15", "2019-09-30"),
}

# streams and variables from rca-data-tools sitesDictionary.csv
STREAMS = {
    "ctd": "4A-CTDPFA{n}03-streamed-ctdpf_optode_sample",
    "ph": "4B-PHSENA{n}02-streamed-phsen_data_record",
    "adcp": "05-ADCPTD{n}02-streamed-adcp_velocity_beam",
}
CTD_VARS = ["sea_water_pressure", "sea_water_temperature", "corrected_dissolved_oxygen"]
ADCP_VARS = ["eastward_seawater_velocity", "northward_seawater_velocity", "bin_depths"]


def stream(site, node, inst):
    n = "1" if site.startswith("RS01") else "3"
    return f"{site}-{node}-{STREAMS[inst].format(n=n)}"


def plot_event(name, site, node, start, end):
    ctd = subset(open_stream(stream(site, node, "ctd")), start, end, CTD_VARS)
    ctd = ctd.resample(time=AVG).mean().compute()
    ph = subset(open_stream(stream(site, node, "ph")), start, end, ["ph_seawater"]).compute()
    adcp = subset(open_stream(stream(site, node, "adcp")), start, end, ADCP_VARS)
    adcp = adcp.isel(bin=slice(0, 28))  # deployedRanges.csv: bins 0-27
    vel = ADCP_VARS[:2]
    adcp[vel] = adcp[vel].where(abs(adcp.eastward_seawater_velocity) < 5)
    adcp = adcp.resample(time=AVG).mean().compute().set_coords("bin_depths")
    adcp = adcp.isel(time=adcp.bin_depths.notnull().all("bin"))  # drop gap hours

    fig, axs = plt.subplots(6, 1, figsize=(12, 14), sharex=True, layout="constrained")
    ctd.sea_water_pressure.plot(ax=axs[0], yincrease=False)
    ctd.sea_water_temperature.plot(ax=axs[1])
    ctd.corrected_dissolved_oxygen.plot(ax=axs[2])
    ph.ph_seawater.where((ph.ph_seawater > 7) & (ph.ph_seawater < 8.5)).plot(ax=axs[3], marker=".", ls="none", ms=2)
    for ax, v in zip(axs[4:], vel):
        adcp[v].plot(ax=ax, x="time", y="bin_depths", yincrease=False, cmap="RdBu_r", vmin=-0.5, vmax=0.5)
        ax.set_ylim(top=20)  # surface sidelobe contamination above ~20 m
    for ax in axs:
        ax.set_title("")
        ax.set_xlabel("")
    fig.suptitle(f"{name}: {site}-{node} ({AVG} means, pH native)")
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / f"{name}.png", dpi=120)
    plt.close(fig)


if __name__ == "__main__":
    for name in sys.argv[1:] or EVENTS:
        plot_event(name, *EVENTS[name])
