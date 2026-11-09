# Axial Seamount: seafloor uplift (BOTPT) and vent fluid (TRHPH), hourly

Data from the NSF Ocean Observatories Initiative (OOI) Regional Cabled Array at
Axial Seamount, {start} to {end}. Every instrument has been averaged into
1-hour bins, so each file has one row per hour.

```
explore.html    START HERE: interactive plots, opens in any web browser
explore.ipynb   starter Jupyter notebook: load, clean, compare, plot
botpt/          seafloor pressure / uplift, 4 sites
trhph/          vent fluid temperature and chloride, 2 probes
plots/          static overview figures
```

**First look:** double-click `explore.html`. Every dataset is stacked on one
time axis (daily means). Drag to zoom, and all panels zoom together, so you can
see what happens at each site at the same moment. Double-click to reset.

**Next step:** open `explore.ipynb` in JupyterLab or VS Code
(`pip install pandas matplotlib jupyterlab`, then `jupyter lab`). It walks
through loading the files, removing glitches, the 2015 eruption, inflation
rates, and comparing uplift with vent temperature, then suggests questions to
explore on your own.

Each dataset comes as a **CSV** (opens in Excel, pandas, R or MATLAB) and a
**netCDF** (same data, plus units and descriptions stored inside the file).

```python
import pandas as pd
df = pd.read_csv("botpt/RS03CCAL-MJ03F-05-BOTPTA301_central_caldera_hourly.csv", parse_dates=["time"])
df.plot(x="time", y="uplift_m")
```

Times are UTC. Hours with no data are kept as blank rows (`n_samples` = 0), so
gaps in the record stay visible.

## BOTPT: seafloor pressure

Pressure sensors on the seafloor (the instrument also measures tilt, which is
not included here). As magma refills the reservoir under Axial,
the seafloor rises and the pressure on top of the sensor drops. Watch for
steady inflation, and for the sudden drop of more than 2 m during the
April 2015 eruption.

| file | site |
|---|---|
| RS03CCAL-MJ03F-05-BOTPTA301 | Central Caldera |
| RS03ECAL-MJ03E-06-BOTPTA302 | Eastern Caldera |
| RS03INT2-MJ03D-06-BOTPTA303 | International District |
| RS03ASHS-MJ03B-09-BOTPTA304 | ASHES vent field (starts Aug 2017) |

| column | units | meaning |
|---|---|---|
| `uplift_m` | m | Seafloor height change since the first day of record. **Positive = up.** Tides removed. Start here. |
| `spike_flag` | 0/1 | 1 = probably a sensor glitch, not real motion. Drop these rows for most work. |
| `seafloor_depth_m` | m | Seafloor depth, positive down, tides removed |
| `predicted_tide_m` | m | The ocean tide that was subtracted (about 2 m from low to high tide) |
| `pressure_dbar` | dbar | Raw bottom pressure, tides **not** removed (1 dbar is about 1 m of water) |
| `n_samples` | count | 15-second samples in the hour (240 = complete hour) |

Things to know:
- Tides were removed by OOI's own processing (the BOTSFLU data product), using
  a tide model, before the hourly averaging. Over a day, the detided record
  varies by a few cm instead of about 2 m.
- What's left after detiding still includes a few cm of ocean signal (currents,
  weather) that every site shares.
- Pressure sensors drift slowly over time, and that drift is **not** corrected.
  It is small next to the inflation signal, but keep it in mind for trends
  under ~1 cm/yr.
- The raw record has short glitches lasting a few hours, where the pressure
  wanders by up to about 1 m and then snaps back. Real seafloor motion doesn't
  snap back like that. `spike_flag` marks any hour more than 0.2 m from the
  running median of the surrounding 2 days. It flags fewer than 200 hours per
  site (most at Eastern Caldera) and does not flag the 2015 eruption.
  `plots/botpt_uplift.png` leaves flagged hours out.
  ```python
  df = df[df.spike_flag == 0]
  ```
- Each site's `uplift_m` starts at its own zero. Compare *changes* between
  sites, not absolute values.

## TRHPH: vent fluid temperature, resistivity and hydrogen probe

A probe placed directly in a hydrothermal vent at the International District
vent field. RS03INT1-MJ03C-10-TRHPHA301 runs 2014 to now;
RS03INT1-MJ03C-09-TRHPHA302 was added in 2023.

| column | units | meaning |
|---|---|---|
| `temperature_mean_degC` | °C | Mean vent fluid temperature in the hour. Start here. |
| `temperature_min_degC`, `temperature_max_degC` | °C | Lowest / highest temperature in the hour |
| `chloride_mmol_kg` | mmol/kg | Vent fluid chloride, calculated from resistivity and temperature. Seawater is about 545. |
| `deployment` | number | OOI deployment number |
| `n_samples` | count | Raw samples in the hour (about 190 = complete hour) |

Things to know:
- **The probe is pulled out and placed in the vent again at each new deployment**
  (roughly once a year, see `deployment` and the dotted lines in
  `plots/trhph_temperature.png`). A jump in temperature at a deployment change
  may come from the new placement, not from the vent changing.
- Long stretches near seawater temperature (around 2 to 30 °C, e.g. 2015, 2021–22,
  2025 on TRHPHA301) usually mean the probe was not sitting in hot vent fluid
  (it was dislodged, or the flow moved), not that the vent cooled. Check the
  deployment dates before reading these as vent behavior.
- TRHPHA302 swings rapidly between about 0 and 350 °C for several months in
  2026 before its new deployment. Treat that stretch with caution.
- Chloride is only calculated when conditions allow, so it is blank much of
  the time, especially for TRHPHA302.
- Fill values and impossible readings (outside -2 to 400 °C, or chloride
  outside 0 to 1000 mmol/kg) were removed before averaging.
- ORP (oxidation-reduction potential, a measure of how chemically reducing
  the fluid is) and hydrogen are not included. ORP is almost entirely fill values, and
  hydrogen is only available as raw sensor voltages.

## Source

OOI Regional Cabled Array data, read from the OOI zarr archive (`s3://ooi-data`).
Built with `requests/2026-11_axial_botpt_trhph/package.py` in the RCA
adhoc-data-requests repo, version `{commit}`. Please acknowledge the NSF Ocean
Observatories Initiative in any presentation or publication that uses these data.
