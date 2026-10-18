"""Export one validated merchandise line table and supporting SQL summaries.

Run after prepare_data.py. No analytical choices differ from the decision log.
The full raw data remain available; only the merchandise dashboard extract is
scoped to paid merchandise lines and cancellation-marked positive-price credits.
"""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3

import pandas as pd

from validate_segment_summaries import load_merchandise, main as validate_segments

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data/processed"


def main():
    validate_segments()
    frame = load_merchandise()
    frame["InvoiceDate"] = pd.to_datetime(frame["InvoiceDate"])
    frame["month_start"] = frame["InvoiceDate"].dt.to_period("M").dt.to_timestamp()
    frame["is_partial_month"] = frame["month_start"].eq(pd.Timestamp("2011-12-01"))
    frame["candidate_same_day_pair_line"] = frame["source_row"].isin([61621, 61626, 540423, 540424])
    frame["missing_customer"] = frame["CustomerID"].isna()
    frame["record_type"] = "Positive sales / charges"
    frame.loc[frame["Quantity"].lt(0), "record_type"] = "Cancellation / credit"
    frame["sensitivity_net_recorded_value"] = frame["sensitivity_positive_value"] - frame["sensitivity_credit_value"]

    # A consistent label avoids splitting a stock code across description variants.
    # Prefer its most frequent positive-line description; lexical order breaks ties.
    labels = (
        frame.loc[frame["Quantity"].gt(0) & frame["Description"].notna()]
        .groupby(["StockCode", "Description"]).size().rename("frequency").reset_index()
        .sort_values(["StockCode", "frequency", "Description"], ascending=[True, False, True])
        .drop_duplicates("StockCode").set_index("StockCode")["Description"]
    )
    fallback = frame.groupby("StockCode")["Description"].first()
    preferred = frame["StockCode"].map(labels).fillna(frame["StockCode"].map(fallback))
    frame["product_label"] = frame["StockCode"] + " | " + preferred.fillna("Description unavailable")
    frame["description_variants"] = frame["StockCode"].map(frame.groupby("StockCode")["Description"].nunique())

    with sqlite3.connect(f"file:{ROOT/'data/retail.sqlite'}?mode=ro", uri=True) as connection:
        monthly = pd.read_sql_query((ROOT / "sql/03_monthly_merchandise.sql").read_text(), connection)
        products = pd.read_sql_query((ROOT / "sql/07_product_summary.sql").read_text(), connection)
        countries = pd.read_sql_query((ROOT / "sql/08_country_summary.sql").read_text(), connection)
        sensitivity = pd.read_sql_query((ROOT / "sql/06_same_day_pair_sensitivity.sql").read_text(), connection)

    value_columns = ["positive_value", "credit_value", "net_recorded_value"]
    python_monthly = frame.groupby("month_start")[value_columns].sum().round(2)
    sql_monthly = monthly.assign(month_start=pd.to_datetime(monthly["month_start"])).set_index("month_start")
    pd.testing.assert_frame_equal(
        python_monthly, sql_monthly[value_columns], check_dtype=False,
        check_exact=False, rtol=0, atol=0.005, check_freq=False,
    )
    positive_invoices = frame.groupby("month_start")["positive_invoice"].nunique()
    pd.testing.assert_series_equal(positive_invoices, sql_monthly["positive_sales_invoices"], check_names=False)

    columns = [
        "source_row", "InvoiceNo", "StockCode", "product_label", "Description",
        "description_variants", "InvoiceDate", "month_start", "Country",
        "Quantity", "UnitPrice", "record_type", "positive_invoice",
        "possible_duplicate", "missing_customer", "is_partial_month",
        "candidate_same_day_pair_line", "positive_value", "credit_value",
        "net_recorded_value", "sensitivity_positive_value", "sensitivity_credit_value",
        "sensitivity_net_recorded_value",
    ]
    export = frame[columns].reset_index(drop=True)
    if len(export) != 536465 or not export["source_row"].is_unique:
        raise ValueError("Export grain or row count failed validation")
    if export["product_label"].isna().any():
        raise ValueError("Missing dashboard product labels")
    if export["candidate_same_day_pair_line"].sum() != 4:
        raise ValueError("Expected exactly four sensitivity lines")
    for column, expected in zip(value_columns, [10271433.06, 478724.18, 9792708.88]):
        if round(export[column].sum(), 2) != expected:
            raise ValueError(f"Export total failed: {column}")

    OUTPUT.mkdir(exist_ok=True)
    path = OUTPUT / "tableau_merchandise.csv"
    temporary = path.with_suffix(".building.csv")
    # Do not use a global two-decimal float format: original UnitPrice includes 0.001.
    export.to_csv(temporary, index=False, encoding="utf-8", date_format="%Y-%m-%d %H:%M:%S")
    reread = pd.read_csv(temporary, dtype={"InvoiceNo": "string", "StockCode": "string"})
    pd.testing.assert_series_equal(reread["InvoiceNo"], export["InvoiceNo"], check_names=False)
    pd.testing.assert_series_equal(reread["StockCode"], export["StockCode"], check_names=False)
    if len(reread) != len(export) or not reread["source_row"].equals(export["source_row"]):
        raise ValueError("CSV record identity round-trip failed")
    for column in value_columns:
        if round(reread[column].sum(), 2) != round(export[column].sum(), 2):
            raise ValueError(f"CSV amount round-trip failed: {column}")
    temporary.replace(path)
    for filename, table in [("monthly_baseline.csv", monthly), ("products.csv", products), ("countries.csv", countries), ("pair_sensitivity.csv", sensitivity)]:
        table.to_csv(OUTPUT / filename, index=False)

    manifest = {
        "exported_at_utc": datetime.now(timezone.utc).isoformat(),
        "file": "data/processed/tableau_merchandise.csv",
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "rows": len(export),
        "grain": "one eligible source merchandise invoice line; source_row retained",
        "coverage": [str(frame["InvoiceDate"].min()), str(frame["InvoiceDate"].max())],
        "partial_month": "December 2011; extract ends 9 December",
        "baseline": {column: round(export[column].sum(), 2) for column in value_columns},
        "checks": {
            "sql_python_product_country_values_and_invoices": "pass",
            "sql_python_monthly_values_and_invoices": "pass",
            "source_row_identity": "pass",
            "csv_identifier_and_value_round_trip": "pass",
            "four_candidate_pair_lines": "pass",
        },
        "product_label": "StockCode plus most frequent description on positive lines; lexical tie-break; first observed description fallback for codes with credits only. Label is not independently verified.",
        "scope": "Merchandise only. Non-merchandise, zero-price and bad-debt records remain in the raw data and audit, outside this dashboard extract.",
    }
    (ROOT / "reports/tableau_export_checks.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"PASS monthly reconciliation and CSV round-trip. Exported {len(export):,} source lines to {path}")


if __name__ == "__main__":
    main()
