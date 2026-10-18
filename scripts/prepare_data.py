"""Prepare unchanged UCI Online Retail records for the guided project.

Run from any directory. Requires pandas and openpyxl. No analytical cleaning,
deduplication, financial filtering or inferred transaction matching is applied.
"""

from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import sqlite3
import zipfile

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
ARCHIVE = RAW / "online_retail.zip"
WORKBOOK = RAW / "Online Retail.xlsx"
CSV = RAW / "online_retail.csv"
DATABASE = ROOT / "data" / "retail.sqlite"
SOURCE_URL = "https://archive.ics.uci.edu/static/public/352/online%2Bretail.zip"
COLUMNS = ["InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate", "UnitPrice", "CustomerID", "Country"]


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    if not WORKBOOK.exists():
        if not ARCHIVE.exists():
            raise SystemExit("Download the UCI source ZIP or Online Retail.xlsx into data/raw first.")
        with zipfile.ZipFile(ARCHIVE) as archive:
            members = [name for name in archive.namelist() if Path(name).name == WORKBOOK.name]
            if len(members) != 1:
                raise ValueError(f"Expected one {WORKBOOK.name} member; found {members}")
            WORKBOOK.write_bytes(archive.read(members[0]))

    frame = pd.read_excel(
        WORKBOOK,
        engine="openpyxl",
        dtype={"InvoiceNo": "string", "StockCode": "string", "CustomerID": "string"},
    )
    if list(frame.columns) != COLUMNS:
        raise ValueError(f"Unexpected source columns: {list(frame.columns)}")
    if len(frame) != 541909:
        raise ValueError(f"Unexpected source size: {len(frame):,}; UCI lists 541,909 invoice lines.")

    # source_row identifies the original worksheet row, including its header row.
    staged = frame.copy()
    staged.insert(0, "source_row", range(2, len(staged) + 2))
    staged["InvoiceDate"] = staged["InvoiceDate"].dt.strftime("%Y-%m-%d %H:%M:%S")
    staged.to_csv(CSV, index=False, encoding="utf-8")

    # Preserve the previously prepared database until the new database is valid.
    temporary = DATABASE.with_suffix(".building.sqlite")
    with sqlite3.connect(temporary) as connection:
        staged.to_sql("raw_transactions", connection, if_exists="replace", index=False, chunksize=10000)
        count, distinct_rows = connection.execute(
            "SELECT COUNT(*), COUNT(DISTINCT source_row) FROM raw_transactions"
        ).fetchone()
        if count != len(frame) or distinct_rows != len(frame):
            raise ValueError("SQLite row-count validation failed.")
        if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("SQLite integrity check failed.")
    temporary.replace(DATABASE)

    csv_check = pd.read_csv(
        CSV,
        dtype={"InvoiceNo": "string", "StockCode": "string", "CustomerID": "string"},
    )
    if len(csv_check) != len(staged):
        raise ValueError("CSV row-count validation failed.")
    for column in ["InvoiceNo", "StockCode", "CustomerID"]:
        if not csv_check[column].equals(staged[column]):
            raise ValueError(f"Identifier round-trip validation failed: {column}")

    manifest = {
        "prepared_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_page": "https://archive.ics.uci.edu/dataset/352/online%2Bretail",
        "source_download": SOURCE_URL,
        "citation": "Chen, D. (2015). Online Retail. UCI Machine Learning Repository. https://doi.org/10.24432/C5BW33",
        "licence": "CC BY 4.0",
        "workbook_sha256": sha256(WORKBOOK),
        "archive_sha256": sha256(ARCHIVE) if ARCHIVE.exists() else None,
        "csv_sha256": sha256(CSV),
        "row_count": len(frame),
        "source_columns": COLUMNS,
        "added_column": "source_row: original worksheet row number, including the header",
        "staging_changes": ["Identifier columns stored as text", "InvoiceDate serialised as ISO timestamp without assigning a timezone", "Added source_row for traceability"],
        "analytical_cleaning": "None; all source records retained",
        "checks": {"source_schema": "pass", "expected_row_count": "pass", "csv_row_count": "pass", "sqlite_row_count": "pass", "identifier_round_trip": "pass", "sqlite_integrity": "pass"},
        "runtime": {"pandas": pd.__version__},
    }
    (ROOT / "data" / "source_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Prepared {len(frame):,} invoice lines; all source records retained.")
    print(f"CSV: {CSV}")
    print(f"SQLite: {DATABASE} (raw_transactions)")
    print("Source schema, record counts, identifier round-trip and database integrity verified.")


if __name__ == "__main__":
    main()
