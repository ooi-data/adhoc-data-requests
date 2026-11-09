# Axial BOTPT + TRHPH hourly data package

Requested Nov 2026 for a VISIONS student: full-record Axial BOTPT
(detided) and TRHPH, packaged for beginners.

- BOTPT, all 4 sites: `botpt_nano_sample_15sec`. Uses OOI's detided
  `botsflu_meandepth`, plus `uplift_m` (positive up, relative to first day) and
  `spike_flag` (> 0.2 m from 49 h running median; catches multi-hour sensor
  artifacts in the source, leaves the 2015 eruption unflagged).
- TRHPH A301 + A302: vent temperature mean/min/max and chloride. Fill values
  masked. ORP and hydrogen are left out (fill values / raw volts).
- 1 h bins, CSV + netCDF per instrument, overview plots, student README
  (`package_README.md`, filled with dates and git version).
- `explore.html`: self-contained plotly page (daily means, linked zoom),
  opens offline with no install.
- `explore.ipynb`: starter notebook (pandas + matplotlib), copied in as is.
  Ships without outputs.

```
uv run python package.py   # -> output/axial_botpt_trhph_hourly_2014-2026-11.zip
```

`END` is fixed, so re-running reproduces the same package unless OOI
reprocesses the source data. Commit before building so the README records a
clean version instead of `-dirty`.
