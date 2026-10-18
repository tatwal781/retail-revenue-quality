# Dashboard and reproducibility verification

Checked on 18 October 2026. Assessment: ready to share with the methodological limitations stated in the findings report.

## Published dashboard

[Retail Sales Quality and Credits](https://public.tableau.com/views/RetailSalesQuality/RetailSalesQuality) loads all four KPI cards, a 13-month trend and two ten-entry ranking charts.

| Scenario | Positive value | Credit value | Net value | Credit ratio |
| --- | ---: | ---: | ---: | ---: |
| Baseline | £10,271,433.06 | £478,724.18 | £9,792,708.88 | 4.66% |
| Exclude two candidate pairs | £10,025,779.86 | £233,070.98 | £9,792,708.88 | 2.32% |

Both selector states were visually checked against these reconciled figures and saved as screenshots. The selector was restored to Baseline. November net value is £1,432,734.99, leading product 22423 is £164,762.19, and the UK is £8,301,718.28. December 2011 is marked partial.

The dashboard uses a fixed desktop layout. Date/country filter controls and a phone-specific layout are not included. Long product descriptions are truncated in chart labels; product codes remain visible.

## Clean reproduction

The preparation and export scripts were rerun in a separate project directory from the original source archive. Source schema, all 541,909 records, identifier round trips and SQLite integrity passed. Independent Python/SQL checks passed for monthly measures, all 3,922 product codes and 38 countries. The export contains 536,465 unique source rows, and its SHA-256 matches the extract input used for the published dashboard.

All 18 code cells in the completed audit notebook were executed sequentially, including category, monthly and segment assertions, without errors. Outputs were regenerated after removing computer-specific paths.

## Packaged workbook

`tableau/Retail Sales Quality.twbx` contains the workbook and its merchandise Hyper extract. ZIP integrity passes. The embedded extract is byte-for-byte identical to the source extract; calculation definitions and dashboard zones are unchanged. File references are relative, and local machine/author fingerprint attributes were removed from the repository copy. The package itself has not undergone a separate native-app rendering check; the source workbook and published dashboard were visually verified.

Raw downloads, staging databases, large CSVs, local paths, intermediate workbook copies and development repair scripts are excluded from the repository. The packaged extract is included deliberately for convenient dashboard review. Dataset attribution and its CC BY 4.0 licence are recorded in the README and source-data notes.
