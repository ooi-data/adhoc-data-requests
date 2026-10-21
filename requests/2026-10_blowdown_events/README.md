# Shallow profiler platform blowdown events

Requested by Deb for Mike (Oct 2026): best blowdown events of the 200 m
platform (PC), with CTD temperature, oxygen, pH and ADCP.

| event | platform | window |
|---|---|---|
| axial_2026 | RS03AXPS-PC03A | 2026-03-01 – 2026-06-30 |
| slope_base_2026 | RS01SBPS-PC01A | 2026-07-01 – 2026-08-31 |
| slope_base_2020 | RS01SBPS-PC01A | 2020-09-01 – 2020-10-31 |
| slope_base_2019 | RS01SBPS-PC01A | 2019-05-15 – 2019-09-30 |

Blowdowns confirmed from CTD pressure (hourly mean > 5 dbar above window median):

| event | max excursion | hours > +5 dbar | span |
|---|---|---|---|
| axial_2026 | +37.0 dbar | 537 | 03-25 – 05-06 |
| slope_base_2026 | +84.5 dbar | 368 | 07-15 – 08-15 |
| slope_base_2020 | +45.5 dbar | 304 | 09-07 – 10-22 |
| slope_base_2019 | +41.1 dbar | 424 | 06-18 – 09-29 |

Plots per event (hourly means): CTDPFA pressure, temperature, corrected O2;
PHSENA pH (native); ADCPTD east/north velocity vs bin depth. Data is read
directly from `s3://ooi-data`; only PNGs are written to `output/`.

```
python blowdown.py              # all events
python blowdown.py axial_2026   # one event
```
