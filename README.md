# adhoc-data-requests

One-off RCA data pulls from the `ooi-data` S3 zarr bucket.

```
common/            shared helpers (open/subset streams)
requests/          one folder per request: YYYY-MM_short-name/
  <request>/README.md   who asked, what, delivery notes
  <request>/*.py        the pull script
  <request>/output/     generated files (gitignored)
```

Reference designators, streams and variables follow
[rca-data-tools params](https://github.com/OOI-CabledArray/rca-data-tools/tree/main/rca_data_tools/qaqc/params).

Environment managed with [uv](https://docs.astral.sh/uv/):

```
uv sync
cd requests/<request> && uv run python <script>.py
```
