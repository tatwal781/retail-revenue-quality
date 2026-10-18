# Analysis Decision Log

Decisions agreed during the guided Python audit. The raw records remain unchanged. The completed audit notebook contains the Python checks and SQL outputs; the scripts independently reconcile the reporting measures.

| Decision | Evidence | Chosen treatment | Rows or value affected | Alternative and limitation |
|---|---|---|---|---|
| Retain missing customer IDs for sales | 135,080 rows lack CustomerID | Include in recorded-value measures; exclude from customer-specific measures | 24.9% of source rows | Customer results describe known IDs only |
| Separate zero-price records | 2,515 rows; all 1,336 negative-quantity lines without a C marker have zero price | Retain in audit; exclude from paid-sales measures | Zero recorded value | Do not infer why goods were free or quantities adjusted |
| Separate bad-debt adjustments | Three records labelled Adjust bad debt, including one positive entry | Exclude all three from sales and credit measures; retain separately | Net -£11,062.06 | Removing only the negative entries would miss the positive adjustment |
| Distinguish cancellation-marked lines | All 9,288 C-prefixed lines have negative quantities | Positive-price C-prefixed negative lines form the cancellation/credit group | Broad signed credit value -£896,812.49 | Does not establish an order cancellation rate or link credits to original sales |
| Retain possible duplicates in baseline | 5,268 repeated rows after first occurrence, excluding source_row | Retain baseline; report a sensitivity excluding repeats | Broad net falls from £9,758,809.99 to £9,737,069.01: -£21,740.98, about 0.22% | Repeated lines may be legitimate; no evidence to confirm errors |
| Separate non-merchandise entries | Descriptions identify postage, fees, discounts, samples, vouchers and manual entries | Map POST/DOT/C2 to delivery; AMAZONFEE/BANK CHARGES/CRUK to fees; M/m to manual; D to discounts; S to samples; gift_ codes to vouchers | Merchandise positive £10,271,433.06; credits -£478,724.18; net £9,792,708.88 | Remaining codes are working merchandise classification, not independently verified product data |
| Use value ratios with explicit denominators | Broad ratio includes fees and other non-merchandise credits | Merchandise ratio = absolute merchandise credit value / positive merchandise value | Approximately 4.66%, compared with broad 8.42% | Not percentage of orders cancelled; no causal explanation of credits |
| Label partial months | Extract ends 9 December 2011 at 12:50 | Show as partial; exclude December 2011 from full-month comparisons | December 2011 | Extract does not prove every other month is operationally complete |
| Define monetary rounding | Python rounds each Quantity × UnitPrice line to two decimals before summing | Use the same per-line rounding in SQL reconciliation; preserve original price | Four source rows have UnitPrice 0.001 and line quantity 1; each rounds to £0.00 | This is an analytical convention; source invoice-level accounting rules are unavailable |

Keep findings separate from assumptions. Record how your totals change when you change a rule.

Category reconciliation passed: SQL run directly against raw_transactions independently reproduced all 21 Python category totals to the penny. The user also ran the notebook comparison and confirmed PASS.

Monthly SQL query returned 13 rows. Monthly positive, credit and net values reconcile to the merchandise category totals in local checks; the user also ran the net-value assertion. December 2011 is flagged as partial. Initial observations are recorded in `reports/interim_findings.md`.

The user completed the invoice concentration check. Three invoices contribute £268,651.60 (56.12%) of all merchandise credits; their individual monthly shares and limits are recorded in `reports/interim_findings.md`.

The user completed the candidate-sale check. January and December each have one candidate 16 and 12 minutes earlier respectively; four April lines have exact candidates roughly 97 days earlier and one has no exact candidate. Same-day evidence is consistent with reversals but does not establish recording errors or explicit links.

The user ran and confirmed the same-day pair sensitivity: four fewer lines; positive and credit values each lower by £245,653.20; net value unchanged; ratio 4.66% in baseline versus 2.32% in the alternative. Baseline retained.

Local segment validation passed using `scripts/validate_segment_summaries.py`: 3,922 stock codes and 38 countries. Five baseline/sensitivity value measures and positive-sales invoice counts agree between SQL and independent Python grouping from the raw CSV. Full totals reconcile to merchandise values; excluding both candidate pair sides leaves every segment's net value unchanged. The full segment results were checked before selecting the top ten.

The user reviewed both top-ten segment tables. Findings are recorded in `reports/findings.md`. The export script also passed independent monthly value/invoice-count checks and CSV round-trip checks. The merchandise Tableau extract has 536,465 rows, one per eligible source line; it retains repeated records and unknown customer IDs. Product labels use the most frequent positive-line description per StockCode, with deterministic ties and a fallback for credit-only codes. Original descriptions and variant counts remain available. Labels do not establish verified product identity.

Completed: dashboard published to Tableau Public, both scenario states visually checked, and screenshots retained. See `reports/dashboard_verification.md`. The packaged workbook embeds the validated extract; raw source records remain unchanged.
