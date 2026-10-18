-- SQLite: monthly merchandise values from raw source records.
-- Baseline retains repeats and missing customer IDs.
-- Filters implement the agreed merchandise and record-type rules.
-- Credit value is displayed as a positive magnitude, not a sale-to-return match.
WITH merchandise_lines AS (
    SELECT
        InvoiceNo,
        DATE(InvoiceDate, 'start of month') AS month_start,
        Quantity,
        ROUND(Quantity * UnitPrice, 2) AS line_value
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
monthly AS (
    SELECT
        month_start,
        SUM(CASE WHEN Quantity > 0 THEN line_value ELSE 0 END)
            AS positive_value,
        -SUM(CASE WHEN Quantity < 0 THEN line_value ELSE 0 END)
            AS credit_value,
        SUM(line_value) AS net_recorded_value,
        COUNT(DISTINCT CASE WHEN Quantity > 0 THEN InvoiceNo END)
            AS positive_sales_invoices
    FROM merchandise_lines
    GROUP BY month_start
)
SELECT
    month_start,
    -- Specific to this extract, which ends on 9 December 2011.
    CASE WHEN month_start = '2011-12-01' THEN 1 ELSE 0 END
        AS is_partial_month,
    ROUND(positive_value, 2) AS positive_value,
    ROUND(credit_value, 2) AS credit_value,
    ROUND(net_recorded_value, 2) AS net_recorded_value,
    ROUND(100.0 * credit_value / NULLIF(positive_value, 0), 2)
        AS credit_to_positive_value_pct,
    positive_sales_invoices
FROM monthly
ORDER BY month_start;
