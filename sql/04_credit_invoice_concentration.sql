-- SQLite: largest merchandise credit invoices in the months under investigation.
-- January and April have elevated full-month credit-to-positive-value ratios.
-- December is partial, but its recorded credits can still be investigated.
-- Baseline retains repeats. This query does not match credits to original sales.
WITH credit_lines AS (
    SELECT
        DATE(InvoiceDate, 'start of month') AS month_start,
        InvoiceNo,
        Quantity,
        ROUND(Quantity * UnitPrice, 2) AS line_value
    FROM raw_transactions
    WHERE Quantity < 0
      AND UnitPrice > 0
      AND UPPER(InvoiceNo) LIKE 'C%'
      AND LOWER(COALESCE(Description, '')) NOT LIKE '%bad debt%'
      AND UPPER(TRIM(StockCode)) NOT IN (
          'POST', 'DOT', 'C2', 'AMAZONFEE', 'BANK CHARGES',
          'CRUK', 'M', 'D', 'S'
      )
      AND SUBSTR(UPPER(TRIM(StockCode)), 1, 5) <> 'GIFT_'
      AND DATE(InvoiceDate, 'start of month') IN (
          '2011-01-01', '2011-04-01', '2011-12-01'
      )
),
invoice_credits AS (
    SELECT
        month_start,
        InvoiceNo,
        -SUM(line_value) AS invoice_credit_value,
        COUNT(*) AS credit_lines,
        -SUM(Quantity) AS credited_units
    FROM credit_lines
    GROUP BY month_start, InvoiceNo
),
ranked AS (
    SELECT
        *,
        SUM(invoice_credit_value) OVER (PARTITION BY month_start)
            AS month_credit_value,
        ROW_NUMBER() OVER (
            PARTITION BY month_start
            ORDER BY invoice_credit_value DESC, InvoiceNo
        ) AS invoice_rank
    FROM invoice_credits
)
SELECT
    month_start,
    invoice_rank,
    InvoiceNo,
    ROUND(invoice_credit_value, 2) AS invoice_credit_value,
    ROUND(month_credit_value, 2) AS month_credit_value,
    ROUND(100.0 * invoice_credit_value / NULLIF(month_credit_value, 0), 2)
        AS share_of_month_credit_pct,
    credit_lines,
    credited_units
FROM ranked
WHERE invoice_rank <= 3
ORDER BY month_start, invoice_rank;
