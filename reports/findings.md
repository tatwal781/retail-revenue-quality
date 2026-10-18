# Retail Sales Quality and Credit Analysis

Historical UCI Online Retail data, 1 December 2010–9 December 2011. Independent portfolio analysis for a hypothetical retail operations manager. The analysis is checked and the [Tableau dashboard is published](https://public.tableau.com/views/RetailSalesQuality/RetailSalesQuality); both scenarios were visually verified on 18 October 2026.

## Answer to the question

The agreed merchandise baseline records £10,271,433.06 in positive value and £478,724.18 in credit value, giving £9,792,708.88 net recorded value. The 4.66% credit-to-positive-value ratio is sensitive to two unusually large candidate same-day sale/credit pairs. Excluding both sides of those pairs in an illustrative sensitivity lowers the ratio to 2.32%, while leaving net value unchanged. Recorded sales are concentrated geographically in the UK, while net value is spread across many products.

## Findings and implications

1. **Classification changes the meaning of the credit ratio.** Across positive sales/charges and cancellation-marked credits, the initial ratio is 8.42%. That includes delivery charges, fees, commissions, manual entries, discounts, samples and vouchers. Merchandise alone gives 4.66%. Bad-debt adjustments and zero-price records remain separately auditable. These are value ratios, not percentages of orders cancelled.

2. **A few invoices dominate merchandise credits.** C541433, C550456 and C581484 contribute £268,651.60, or 56.12% of all merchandise credit value. Their shares of January, April and partial December credit value are 84.33%, 69.03% and 96.75% respectively. Investigating these events is more informative than assuming a widespread increase in cancellations.

3. **Two large events have exact candidate same-day positive lines.** The January and December candidates match customer, stock code, opposite quantity and unit price, and occur 16 and 12 minutes before the credit. Both positive and credit values fall by £245,653.20 when all four lines are excluded in the alternative scenario. Net merchandise value stays £9,792,708.88. This is consistent with same-day reversals, without proving recording errors or explicit links. Four April lines have exact candidates around 97 days earlier; one has none under the matching rule.

4. **The UK accounts for 84.77% of net merchandise value**, or £8,301,718.28. Its credit ratio is 5.10% in the baseline and 2.35% in the candidate-pair sensitivity. The Netherlands, EIRE, Germany and France are the next largest recorded countries by net value. These describe the retailer's extract, not national market sizes or evidence for international expansion.

5. **The leading ten products contribute £798,620.86, or 8.16% of net merchandise value.** StockCode 22423 leads at £164,762.19, approximately 1.68% of the total. Product identity is grouped by StockCode because descriptions can vary. The 5.57% credit ratio for 22423 and 6.34% for 85123A justify inspecting their invoices alongside their substantial value; different product mixes and volumes limit direct performance comparisons.

6. **November has the highest net merchandise value among the months not flagged as partial**, at £1,432,734.99. January's full-month credit ratio is 13.62%, followed by April at 6.45%. December 2011 ends on 9 December; its approximately 28.29% ratio and raw monthly sales total should not be treated as a complete-month result. One historical year cannot establish recurring seasonality or explain why monthly values differ.

## Recommended follow-up for the hypothetical manager

- Review original documents or explicit references for the three concentrated credit invoices. Confirm the relationship between the two candidate same-day pairs before treating them as corrections; document any confirmed changes to reporting rules.
- Keep merchandise, delivery and financial adjustments separately identifiable. Present the retained-record baseline with a clearly labelled sensitivity so readers can see the effect of large matched candidates.
- Inspect credit concentration and source documents for high-value product codes before proposing operational changes. Review the underlying invoices behind Spain's 7.11% ratio and Japan's 5.34% ratio rather than ranking countries on percentages alone.
- Use the UK concentration and leading-product values to prioritise further operational review. Validate demand across additional years before making seasonal forecasts or stock-planning claims.

These are proposed investigations. No process change, cost saving, revenue increase or reduction in credits was implemented or measured.

## Method and limits

The source has 541,909 invoice lines, not orders. The merchandise extract contains 536,465 eligible lines with positive prices, using the agreed stock-code classification and positive-sale/C-prefixed-credit rules. All records remain available in the raw data. Missing customer IDs are retained for sales; 135,080 source lines (24.9%) lack an ID, limiting customer analysis. Merchandise classification and descriptive labels are working rules, not independently verified product taxonomy.

Possible duplicates remain in the baseline. Excluding repeated source records in the broader recorded-value sensitivity changes net value by £21,740.98, approximately 0.22%; repetition alone does not prove an error. This duplicate comparison is separate from the two-candidate-pair sensitivity.

Python and SQL agree on category totals, monthly/product/country values and the checked positive-sales invoice counts. Monetary values round Quantity × UnitPrice to two decimals per line before aggregation. The original sub-penny unit prices are preserved. Customer, stock code, quantity, price and timing provide candidate-match evidence; they do not establish intent, cause or an explicit credit-to-sale reference. Credits can relate to sales in other periods. Costs, profit and the causes of credits are unavailable.

Source: Chen, D. (2015), [Online Retail, UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/352/online%2Bretail), [DOI](https://doi.org/10.24432/C5BW33), CC BY 4.0. Decision details and investigative results are in decision_log.md and interim_findings.md; export checks are in tableau_export_checks.json.
