"""Reconcile product/country SQL with independently grouped raw CSV records.

Run from any directory after prepare_data.py. Uses only pandas and SQLite.
Baseline monetary convention: round each line to two decimals, then aggregate.
"""

from decimal import Decimal
from pathlib import Path
import sqlite3

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
METRICS = [
    "positive_value", "credit_value", "net_recorded_value",
    "sensitivity_positive_value", "sensitivity_credit_value",
]
TOTALS = ["10271433.06", "478724.18", "9792708.88", "10025779.86", "233070.98"]


def load_merchandise():
    raw = pd.read_csv(
        ROOT / "data/raw/online_retail.csv",
        dtype={"InvoiceNo": "string", "StockCode": "string", "CustomerID": "string"},
    )
    code = raw["StockCode"].str.strip().str.upper()
    raw["possible_duplicate"] = raw.drop(columns="source_row").duplicated()
    cancellation = raw["InvoiceNo"].str.upper().str.startswith("C", na=False)
    eligible = (
        raw["UnitPrice"].gt(0)
        & ((raw["Quantity"].gt(0) & ~cancellation)
           | (raw["Quantity"].lt(0) & cancellation))
        & ~raw["Description"].str.contains("bad debt", case=False, na=False)
        & ~code.isin(["POST", "DOT", "C2", "AMAZONFEE", "BANK CHARGES", "CRUK", "M", "D", "S"])
        & ~code.str.startswith("GIFT_", na=False)
    )
    frame = raw.loc[eligible].copy()
    frame["net_recorded_value"] = (frame["Quantity"] * frame["UnitPrice"]).round(2)
    frame["positive_value"] = frame["net_recorded_value"].where(frame["Quantity"].gt(0), 0)
    frame["credit_value"] = -frame["net_recorded_value"].where(frame["Quantity"].lt(0), 0)
    keep = ~frame["source_row"].isin([61621, 61626, 540423, 540424])
    frame["sensitivity_positive_value"] = frame["positive_value"].where(keep, 0)
    frame["sensitivity_credit_value"] = frame["credit_value"].where(keep, 0)
    frame["positive_invoice"] = frame["InvoiceNo"].where(frame["Quantity"].gt(0))
    return frame


def main():
    frame = load_merchandise()

    database = ROOT / "data/retail.sqlite"
    with sqlite3.connect(f"file:{database}?mode=ro", uri=True) as connection:
        for key, filename in [("StockCode", "07_product_summary.sql"), ("Country", "08_country_summary.sql")]:
            sql = pd.read_sql_query((ROOT / "sql" / filename).read_text(), connection).set_index(key)
            python = frame.groupby(key)[METRICS].sum().round(2)
            # SQLite returns text as object; CSV identifiers use pandas StringDtype.
            # Compare identifier values and numbers without requiring identical storage dtypes.
            pd.testing.assert_frame_equal(
                sql[METRICS].sort_index(), python.sort_index(),
                check_dtype=False, check_index_type=False,
                check_exact=False, rtol=0, atol=0.005,
            )
            counts = frame.groupby(key)["positive_invoice"].nunique()
            pd.testing.assert_series_equal(
                sql["positive_sales_invoices"].sort_index(), counts.sort_index(),
                check_names=False, check_index_type=False,
            )
            if not sql.index.is_unique or sql["baseline_lines"].sum() != 536465:
                raise ValueError(f"{key}: segment identity/line-count check failed")
            for metric, expected in zip(METRICS, TOTALS):
                actual = sum(Decimal(str(value)) for value in sql[metric])
                if actual != Decimal(expected):
                    raise ValueError(f"{key}: {metric} total does not reconcile: {actual}")
            difference = sql["sensitivity_positive_value"] - sql["sensitivity_credit_value"] - sql["net_recorded_value"]
            if not difference.abs().lt(0.005).all():
                raise ValueError(f"{key}: paired exclusion unexpectedly changes a segment's net value")
            print(f"PASS {key}: {len(sql):,} groups; five value measures and invoice counts agree between Python and SQL; totals reconcile.")


if __name__ == "__main__":
    main()
