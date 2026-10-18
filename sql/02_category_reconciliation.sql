-- SQLite. Read-only reconciliation against the original staging table.
-- Reimplement the agreed Python rules; do not import Python's category labels.
-- Preserve repeats and missing customer IDs in this baseline.
-- Monetary convention: round each line to two decimals, then aggregate.
WITH classified AS (
    SELECT
        ROUND(Quantity * UnitPrice, 2) AS line_value,
        CASE
            WHEN LOWER(COALESCE(Description, '')) LIKE '%bad debt%'
                THEN 'Bad-debt adjustment'
            WHEN UnitPrice = 0
                THEN 'Zero-price record'
            WHEN Quantity < 0 AND UnitPrice > 0
                 AND UPPER(InvoiceNo) LIKE 'C%'
                THEN 'Cancellation / credit'
            WHEN Quantity > 0 AND UnitPrice > 0
                 AND UPPER(InvoiceNo) NOT LIKE 'C%'
                THEN 'Positive sales / charges'
            ELSE 'Needs review'
        END AS record_type,
        CASE
            WHEN LOWER(COALESCE(Description, '')) LIKE '%bad debt%'
                THEN 'Bad-debt adjustments'
            WHEN UPPER(TRIM(StockCode)) IN ('POST', 'DOT', 'C2')
                THEN 'Delivery charges'
            WHEN UPPER(TRIM(StockCode)) IN ('AMAZONFEE', 'BANK CHARGES', 'CRUK')
                THEN 'Fees and commissions'
            WHEN UPPER(TRIM(StockCode)) = 'M' THEN 'Manual entries'
            WHEN UPPER(TRIM(StockCode)) = 'D' THEN 'Discounts'
            WHEN UPPER(TRIM(StockCode)) = 'S' THEN 'Samples'
            WHEN SUBSTR(UPPER(TRIM(StockCode)), 1, 5) = 'GIFT_'
                THEN 'Gift vouchers'
            ELSE 'Merchandise'
        END AS item_category
    FROM raw_transactions
)
SELECT
    item_category,
    ROUND(SUM(CASE WHEN record_type = 'Positive sales / charges'
                   THEN line_value ELSE 0 END), 2) AS "Positive sales / charges",
    ROUND(SUM(CASE WHEN record_type = 'Cancellation / credit'
                   THEN line_value ELSE 0 END), 2) AS "Cancellation / credit",
    ROUND(SUM(line_value), 2) AS "Net recorded value"
FROM classified
WHERE record_type IN ('Positive sales / charges', 'Cancellation / credit')
GROUP BY item_category
ORDER BY item_category;
