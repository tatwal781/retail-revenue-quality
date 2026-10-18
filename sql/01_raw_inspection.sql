-- SQLite. Read-only source profiling; invoice lines are not orders.
SELECT * FROM raw_transactions LIMIT 10;

SELECT
    COUNT(*) AS invoice_lines,
    COUNT(DISTINCT InvoiceNo) AS distinct_invoices,
    COUNT(DISTINCT CustomerID) AS known_customers,
    MIN(InvoiceDate) AS earliest_date,
    MAX(InvoiceDate) AS latest_date,
    SUM(CustomerID IS NULL) AS missing_customer_lines,
    SUM(Description IS NULL) AS missing_description_lines,
    SUM(Quantity < 0) AS negative_quantity_lines,
    SUM(UnitPrice = 0) AS zero_price_lines,
    SUM(UnitPrice < 0) AS negative_price_lines,
    SUM(UPPER(InvoiceNo) LIKE 'C%') AS cancellation_marked_lines
FROM raw_transactions;
