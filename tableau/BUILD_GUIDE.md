# Tableau build — Retail Sales Quality and Credits

The dashboard uses historical UCI Online Retail data, scoped to merchandise. This is an independent portfolio project with a hypothetical retail manager as the audience.

## 1. Connect one line-level source

In Tableau, choose **Connect → Text File**, then open:

`data/processed/tableau_merchandise.csv`

Use this single line-level table for all dashboard sheets. The other processed CSVs are reference summaries, not extra tables to join: joining them could multiply invoice lines. The source has 536,465 merchandise lines, including repeats and lines with unknown customers. Original identifiers are retained.

Check types: InvoiceNo and StockCode are strings/dimensions; InvoiceDate is Date & Time; month_start is a date; value columns are decimal numbers; is_partial_month and candidate_same_day_pair_line are Boolean. Keep UnitPrice's source precision; three merchandise records have a price of 0.001. Financial measures use the documented two-decimal line rounding.

`product_label` combines StockCode and the most frequent description on positive lines, with a lexical tie-break and an observed-description fallback for codes with credits only. It gives one label per code; it does not establish a verified product name. The SQL summary's `example_description` is a different, explicitly illustrative label. Use product_label in the dashboard to avoid splitting one code across description variants.

## 2. Create the scenario parameter

Create a String parameter called **Scenario**, allowing a List:

- `Baseline`
- `Exclude two candidate pairs`

Default to Baseline and show the parameter control. It must be referenced by calculations to affect the dashboard.

Create these calculated fields. Insert fields from the Data pane if Tableau displays their names with spaces rather than underscores.

**Selected positive value**

```tableau
IF [Scenario] = 'Baseline' THEN [positive_value]
ELSE [sensitivity_positive_value]
END
```

**Selected credit value**

```tableau
IF [Scenario] = 'Baseline' THEN [credit_value]
ELSE [sensitivity_credit_value]
END
```

**Selected net value**

```tableau
[Selected positive value] - [Selected credit value]
```

**Credit-to-sales value ratio**

```tableau
IF SUM([Selected positive value]) <> 0 THEN
    SUM([Selected credit value]) / SUM([Selected positive value])
END
```

Format the last field as a percentage with two decimals. It already returns a proportion: do not multiply by 100 as well. Calculate the ratio from sums; never average individual-line ratios or the precomputed country/product percentages.

## 3. Check four KPI sheets before chart design

Use SUM for the selected positive, credit and net fields. The ratio is already an aggregate calculation. With no filters:

| Scenario | Positive value | Credit value | Net value | Credit-to-sales value ratio |
|---|---:|---:|---:|---:|
| Baseline | £10,271,433.06 | £478,724.18 | £9,792,708.88 | 4.66% |
| Exclude two candidate pairs | £10,025,779.86 | £233,070.98 | £9,792,708.88 | 2.32% |

Display credit value as a positive magnitude, and explain that net = positive value minus credits. This is recorded merchandise value, not profit. Keep repeats in both parameter scenarios; the duplicate sensitivity is a separate audit, not this parameter.

## 4. Build three views

1. **Monthly net merchandise value:** month_start on Columns at Month-and-Year detail and continuous date; SUM(Selected net value) on Rows; line marks. Check for 13 points rather than combining December 2010 and December 2011. Label December 2011 as partial, ending 9 December; do not infer a full-month decline from that point. Include selected positive value, selected credit value and the ratio in tooltips.
2. **Top 10 products by net merchandise value:** product_label on Rows; SUM(Selected net value) on Columns; horizontal bars descending. Apply a Top 10 by SUM(Selected net value) filter to this sheet only. Include StockCode, selected credit value and the ratio in tooltips.
3. **Top 10 recorded countries by net merchandise value:** Country on Rows; SUM(Selected net value) on Columns; horizontal bars descending. Apply a Top 10 filter to this sheet only. Include selected positive/credit values and the ratio in tooltips. Country labels are recorded source values; EIRE is preserved. This chart describes this retailer, not national market size.

Use £ number formatting; the source prices are in sterling. Use one dark blue for value bars/lines and orange for credit annotations. Labels, captions and tooltips should carry meaning without depending only on colour.

## 5. Assemble the published dashboard

Create a dashboard around 1400 × 900 with a title and date coverage, four KPI cards across the top, the monthly chart below, then product/country bars alongside each other. Include the Scenario control. The published version shows all countries and the full period. Start with all countries and the full extract so totals match the reference above.

Optional extension, not included in the current published version: apply shared Country/date filters to all relevant sheets. If using Top N filters, add Country/date filters to context on the ranked sheets so Top N is calculated for the selected scope. Keep the Top 10 product/country restrictions local to their chart: they must not limit the whole-dashboard KPIs. If adding a partial-month filter, apply it consistently and let viewers see that the scope changed.

Suggested footer: `Historical UCI Online Retail data, 1 Dec 2010–9 Dec 2011. Merchandise only. December 2011 is partial. Credit ratio measures value, not the percentage of orders cancelled. Candidate-pair exclusions are an illustrative sensitivity; baseline retains all eligible records.`

## 6. Verify before sharing

- Baseline and alternative KPIs match the table above with all filters cleared.
- Changing the parameter updates positive/credit values and their ratio while full-period net value stays unchanged.
- Monthly chart agrees with monthly_baseline.csv in baseline; November net is £1,432,734.99.
- Baseline UK net is £8,301,718.28. Its ratio is 5.10%, or 2.35% in the candidate-pair sensitivity.
- The leading net-value product is StockCode 22423 at £164,762.19; labels may differ from the SQL's illustrative description.
- Top 10 chart restrictions do not restrict the KPI cards. If adding country/date filters, verify they affect every intended sheet.
- Tooltips identify historical scope, values and ratio definitions. Treat UK and product concentration as descriptive findings; do not claim proven cancellation causes or improvements delivered.

The finished `Retail Sales Quality.twbx` contains an embedded Hyper extract. Download it, open in Tableau, and use the Scenario selector. Both states are checked in `reports/dashboard_verification.md`. For source refresh, first rebuild `data/processed/tableau_merchandise.csv`, then replace the workbook connection with that CSV and recreate its extract. The original source CSV is deliberately excluded from the package. Published version: https://public.tableau.com/views/RetailSalesQuality/RetailSalesQuality

## Official Tableau references

- [Connect to a text file](https://help.tableau.com/current/pro/desktop/en-us/examples_text.htm)
- [Create parameters](https://help.tableau.com/current/pro/desktop/en-us/parameters_create.htm)
- [Create calculated fields](https://help.tableau.com/current/pro/desktop/en-us/calculations_calculatedfields_create.htm)
- [Filter order of operations and Top N](https://help.tableau.com/current/pro/desktop/en-us/order_of_operations.htm)
