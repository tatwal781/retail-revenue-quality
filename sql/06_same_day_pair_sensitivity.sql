-- SQLite: illustrative sensitivity, NOT a replacement for the baseline.
-- Candidate pairs from query 05:
-- 541431 / C541433: source rows 61621 and 61626; 16 minutes apart.
-- 581483 / C581484: source rows 540423 and 540424; 12 minutes apart.
-- Each has an exact known-customer/product/opposite-quantity/price match.
-- There is no explicit source link proving a reversal or recording error.
-- Exclude both positive and credit lines together in the alternative scenario.
WITH merchandise AS (
    SELECT
        source_row,
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
scenario_lines AS (
    SELECT 'Baseline: all merchandise records' AS scenario, Quantity, line_value
    FROM merchandise
    UNION ALL
    SELECT 'Sensitivity: exclude two candidate same-day pairs', Quantity, line_value
    FROM merchandise
    WHERE source_row NOT IN (61621, 61626, 540423, 540424)
),
totals AS (
    SELECT
        scenario,
        COUNT(*) AS retained_lines,
        SUM(CASE WHEN Quantity > 0 THEN line_value ELSE 0 END)
            AS positive_value,
        -SUM(CASE WHEN Quantity < 0 THEN line_value ELSE 0 END)
            AS credit_value,
        SUM(line_value) AS net_recorded_value
    FROM scenario_lines
    GROUP BY scenario
)
SELECT
    scenario,
    retained_lines,
    ROUND(positive_value, 2) AS positive_value,
    ROUND(credit_value, 2) AS credit_value,
    ROUND(net_recorded_value, 2) AS net_recorded_value,
    ROUND(100.0 * credit_value / NULLIF(positive_value, 0), 2)
        AS credit_to_positive_value_pct
FROM totals
ORDER BY scenario;
