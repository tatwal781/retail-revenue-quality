# Interim findings — guided project in progress

These are descriptive findings from the agreed baseline. They are not final recommendations or evidence of implemented business improvements. All source records are retained; bad debt and zero-price lines are separated from paid sales and credits. Merchandise is a working stock-code classification.

## Validated baseline

- Merchandise positive value: £10,271,433.06.
- Merchandise credit value, expressed as a positive magnitude: £478,724.18.
- Net recorded merchandise value: £9,792,708.88.
- Merchandise credit-to-positive-value ratio: 4.66%.
- The broader 8.42% ratio includes delivery, fees and other non-merchandise entries. Neither ratio is a percentage of orders cancelled.
- All 21 category totals agree between Python and SQL, including the user's notebook assertion.

## Monthly observations

- November 2011 has the highest net merchandise value among the calendar months not flagged as partial: £1,432,734.99. One historical year cannot establish a recurring seasonal pattern or explain the increase.
- January 2011's merchandise credit-to-positive-value ratio is 13.62%, with £91,526.30 in credits.
- April 2011's ratio is 6.45%, with £33,316.91 in credits.
- December 2011 ends on 9 December at 12:50. Its recorded merchandise credits are £174,126.76 against £615,493.27 in positive value: approximately 28.29%. Do not compare its raw monthly sales total with full months or extrapolate it to the end of December.
- Credits in any month may relate to sales in another period. No sale-to-credit matching has been established.

## Next investigation

The user ran `sql/04_credit_invoice_concentration.sql`. Shares use all merchandise credits in each selected month before selecting the top three invoices.

| Credit invoice | Month | Value | Share of that month's merchandise credits |
|---|---|---:|---:|
| C541433 | January 2011 | £77,183.60 | 84.33% |
| C550456 | April 2011 | £22,998.40 | 69.03% |
| C581484 | Partial December 2011 | £168,469.60 | 96.75% |

Together these three invoices account for £268,651.60, approximately 56.12% of all £478,724.18 in merchandise credit value across the extract. Elevated monthly ratios are concentrated in a small number of events; the results do not establish why those events occurred.

The user ran `sql/05_large_credit_sale_candidates.sql`, looking for earlier positive lines with the same known customer, stock code, opposite quantity and equal unit price. All matches and their counts remain visible:

- C541433 has one candidate positive line on invoice 541431, 16 minutes earlier on 18 January. Source rows: credit 61626, candidate sale 61621. Both values have magnitude £77,183.60.
- C581484 has one candidate positive line on invoice 581483, 12 minutes earlier on 9 December. Source rows: credit 540424, candidate sale 540423. Both values have magnitude £168,469.60.
- Four of the five lines on C550456 have one exact candidate each from 11 January, roughly 97 days before the April credit. The fifth has no exact candidate under this rule.

The January and December evidence is consistent with same-day reversals. It does not establish a recording error, intent or an explicit sale-to-credit relationship. A non-match does not prove that no related sale exists: quantities could be split, references could differ, or sales could be outside the extract. Large records remain in the baseline.

`sql/06_same_day_pair_sensitivity.sql` provides an explicitly labelled alternative excluding both the positive and credit line from each of the two candidate same-day pairs, not just the negative entries. It does not exclude the April invoice or replace the baseline. This comparison tests how event concentration affects the value ratio while keeping the classification rule visible.

The user ran the sensitivity and confirmed: retained lines fall from 536,465 to 536,461; positive value falls to £10,025,779.86 and credits to £233,070.98. The value ratio changes from 4.66% to 2.32%, while net merchandise value stays £9,792,708.88. Both positive and credit values fall by £245,653.20. The baseline is unchanged.

Next, `sql/07_product_summary.sql` and `sql/08_country_summary.sql` provide full product and country aggregates with baseline values and explicitly labelled sensitivity values. Products are grouped by StockCode, not Description; the example description is only a label. Shares use total merchandise net value across the whole extract. Segment ratios can be undefined where the positive-value denominator is zero. Source-country comparisons do not measure national market size. Removing exact opposite pairs should leave each affected segment's net value unchanged while potentially changing its value ratio.

The user reviewed product and country tables. UK net merchandise value is £8,301,718.28 (84.77%); its ratio changes from 5.10% to 2.35% in the candidate-pair sensitivity. The ten leading products total £798,620.86 (8.16% of net merchandise value). The checked findings and proposed follow-up investigations are now in `reports/findings.md`.

`scripts/export_tableau_data.py` independently reconciled monthly values and positive invoice counts against SQL, in addition to the product/country cross-checks. It exported 536,465 merchandise lines with baseline/sensitivity measures and consistent product labels, and validated the CSV identifier/value round-trip. See `reports/tableau_export_checks.json`.

Next: follow `tableau/BUILD_GUIDE.md`. The Tableau workbook, dashboard screenshots and final visual review remain to complete. The data-export script does not create or publish a Tableau dashboard.
