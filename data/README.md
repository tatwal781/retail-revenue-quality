# Source data

Chen, D. (2015), **Online Retail**, UCI Machine Learning Repository.

- [Dataset page](https://archive.ics.uci.edu/dataset/352/online%2Bretail)
- [DOI](https://doi.org/10.24432/C5BW33)
- Licence: [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/).
- Original coverage: 1 December 2010 to 9 December 2011.
- Original size: 541,909 invoice lines, eight source columns.

Download `Online Retail.xlsx` or the source ZIP into `data/raw/` (create the folder if needed). If using the ZIP, name it `online_retail.zip`. Run the preparation and export commands in the main README. The scripts preserve source rows and identifiers; analytical exclusions are applied to reporting outputs, not the raw source.

The raw workbook/ZIP, staging database and generated CSVs are excluded from version control. `source_manifest.json` records source hashes and checks. The Tableau package includes the validated merchandise extract so the dashboard can be opened without rebuilding the data.
