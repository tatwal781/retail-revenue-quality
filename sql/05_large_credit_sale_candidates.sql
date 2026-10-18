-- SQLite: candidate earlier positive lines for the three largest credit events.
-- Match on known customer, stock code, exact opposite quantity and same unit price.
-- Preserve all candidate matches and count them; never force a one-to-one link.
-- This is investigative evidence, not an explicit credit-to-sale reference.
-- Source-row IDs identify both lines; missing customer IDs cannot establish a match.
WITH target_credits AS (
    SELECT
        source_row,
        InvoiceNo,
        StockCode,
        Description,
        Quantity,
        InvoiceDate,
        UnitPrice,
        CustomerID
    FROM raw_transactions
    WHERE InvoiceNo IN ('C541433', 'C550456', 'C581484')
      AND Quantity < 0
      AND UnitPrice > 0
)
SELECT
    c.source_row AS credit_source_row,
    c.InvoiceNo AS credit_invoice,
    c.StockCode,
    c.Description,
    c.InvoiceDate AS credit_date,
    -c.Quantity AS credited_units,
    ROUND(-c.Quantity * c.UnitPrice, 2) AS credit_value,
    c.CustomerID,
    s.source_row AS candidate_sale_source_row,
    s.InvoiceNo AS candidate_sale_invoice,
    s.InvoiceDate AS candidate_sale_date,
    ROUND((JULIANDAY(c.InvoiceDate) - JULIANDAY(s.InvoiceDate)) * 1440.0, 1)
        AS minutes_between,
    COUNT(s.source_row) OVER (PARTITION BY c.source_row)
        AS candidate_count
FROM target_credits AS c
LEFT JOIN raw_transactions AS s
    ON s.CustomerID = c.CustomerID
   AND s.StockCode = c.StockCode
   AND s.Quantity = -c.Quantity
   AND s.UnitPrice = c.UnitPrice
   AND s.Quantity > 0
   AND UPPER(s.InvoiceNo) NOT LIKE 'C%'
   AND s.InvoiceDate <= c.InvoiceDate
ORDER BY c.InvoiceDate, c.source_row, s.InvoiceDate, s.source_row;
