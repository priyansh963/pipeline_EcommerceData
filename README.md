# Shop orders pipeline: revenue by category

**Purpose.** This small, reproducible Python pipeline extends the Chapter 2 shop-order exercise with a clean-orders output and a new `revenue_by_category.csv` aggregate. It keeps rejected rows for review and never changes the raw input.

## Group members

| Name | Role |
|---|---|
| Priyansh (account owner; replace with full name) | Pipeline, documentation, and versioning |
| Add group member | Add contribution |
| Add group member | Add contribution |

Update this table with the actual full names and contributions before submission.

## Files

- `data/raw/orders_2024_03.csv`: March source export (32 rows), preserved as received.
- `data/raw/customers.csv`: accompanying customer master source file; not joined in this pipeline.
- `src_pipeline.py`: validation, cleaning, quarantine, and category aggregation.
- `data/processed/clean_orders.csv`: accepted orders, normalized date/currency, with row revenue.
- `data/processed/revenue_by_category.csv`: order count and EUR revenue for each category.
- `data/quarantine/rejected_orders.csv`: rejected source records and reasons.
- `logs/run_log.txt`: latest run counts and rejection summary.
- `docs/data_dictionary.md`, `docs/cleaning_log.md`, `docs/lineage.md`: documentation.

## Run

Requires Python 3.10 or newer; no third-party packages are needed.

```bash
python src_pipeline.py
```

The pipeline accepts ISO (`YYYY-MM-DD`), dotted (`DD.MM.YYYY`), and US slash (`MM/DD/YYYY`) order dates, and treats `€` as EUR. It reports malformed dates and numeric values in quarantine rather than stopping the complete run. The custom date rule uses the machine's current local date.

## Validation rules

1. `order_id` must exist and be unique within the input.
2. `order_date` must parse and must not be in the future (custom business check).
3. `quantity` must be an integer from 1 to 100 inclusive.
4. `unit_price` must be present and non-negative.
5. Only EUR is included in this output; other currencies are quarantined because no exchange-rate policy was supplied.
6. `category` must be present.

See `docs/cleaning_log.md` for the decisions and `docs/lineage.md` for the pipeline drawing.

## Source and limitations

The raw files were copied from the supplied `Lab2.5_Materials/chapter2/data` course exercise. Source values are retained; this repository contains only the March orders for the requested category output. The pipeline does not infer foreign-exchange rates, enrich customer attributes, or impute missing prices. Ask the course team whether the course materials require a specific attribution/license statement.

## Version history

See `git log --oneline` for the implementation history. Add the public group-repository URL here once the group repository is identified.
