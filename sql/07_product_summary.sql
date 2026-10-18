-- SQLite. One row per stock code; descriptions do not define product identity.
-- Example description is a label, not a verified canonical product name.
-- Baseline retains repeats and the two candidate same-day pairs.
-- Sensitivity excludes source rows 61621, 61626, 540423, 540424 only.
WITH merchandise AS (
    SELECT
        StockCode, Description, InvoiceNo, Quantity,
        ROUND(Quantity * UnitPrice, 2) AS line_value,
        CASE WHEN source_row IN (61621, 61626, 540423, 540424)
             THEN 1 ELSE 0 END AS candidate_pair_line
    FROM raw_transactions
    WHERE UnitPrice > 0
      AND (
          (Quantity > 0 AND UPPER(InvoiceNo) NOT LIKE 'C%')
          OR (Quantity < 0 AND UPPER(InvoiceNo) LIKE 'C%')
      )
      AND LOWER(COALESCE(Description, '')) NOT LIKE '%bad debt%'
      AND UPPER(TRIM(StockCode)) NOT IN (
          'POST', 'DOT', 'C2', 'AMAZONFEE', 'BANK CHARGES',
          'CRUK', 'M', 'D', 'S'
      )
      AND SUBSTR(UPPER(TRIM(StockCode)), 1, 5) <> 'GIFT_'
),
totals AS (
    SELECT
        StockCode,
        MIN(Description) AS example_description,
        COUNT(DISTINCT Description) AS description_variants,
        COUNT(*) AS baseline_lines,
        COUNT(DISTINCT CASE WHEN Quantity > 0 THEN InvoiceNo END)
            AS positive_sales_invoices,
        SUM(CASE WHEN Quantity > 0 THEN line_value ELSE 0 END)
            AS positive_value,
        -SUM(CASE WHEN Quantity < 0 THEN line_value ELSE 0 END)
            AS credit_value,
        SUM(line_value) AS net_recorded_value,
        SUM(CASE WHEN Quantity > 0 AND candidate_pair_line = 0
                 THEN line_value ELSE 0 END) AS sensitivity_positive_value,
        -SUM(CASE WHEN Quantity < 0 AND candidate_pair_line = 0
                  THEN line_value ELSE 0 END) AS sensitivity_credit_value
    FROM merchandise
    GROUP BY StockCode
)
SELECT
    StockCode,
    example_description,
    description_variants,
    baseline_lines,
    positive_sales_invoices,
    ROUND(positive_value, 2) AS positive_value,
    ROUND(credit_value, 2) AS credit_value,
    ROUND(net_recorded_value, 2) AS net_recorded_value,
    ROUND(100.0 * net_recorded_value /
          NULLIF(SUM(net_recorded_value) OVER (), 0), 2) AS net_value_share_pct,
    ROUND(100.0 * credit_value / NULLIF(positive_value, 0), 2)
        AS credit_to_positive_value_pct,
    ROUND(sensitivity_positive_value, 2) AS sensitivity_positive_value,
    ROUND(sensitivity_credit_value, 2) AS sensitivity_credit_value,
    ROUND(100.0 * sensitivity_credit_value /
          NULLIF(sensitivity_positive_value, 0), 2)
        AS sensitivity_credit_to_positive_value_pct
FROM totals
ORDER BY net_recorded_value DESC, StockCode;
