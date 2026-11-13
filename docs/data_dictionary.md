# Data dictionary

## `clean_orders.csv`

| Column | Type | Meaning / handling |
|---|---|---|
| order_id | text | Source order identifier; must be nonblank and unique. |
| order_date | ISO date | Source date normalized to `YYYY-MM-DD`; future or invalid dates rejected. |
| customer_id | text | Source customer identifier; carried through without master-data join. |
| customer_name | text | Source customer name; retained as supplied, including blanks. |
| city | text | Source city; retained as supplied. |
| country | text | Source country; retained as supplied. |
| category | text | Source category; required for aggregation. |
| quantity | integer | Units; only 1–100 accepted. |
| unit_price | decimal EUR | Non-negative source unit price with two decimals. |
| currency | text | Accepted output is normalized to `EUR`; other currencies are rejected. |
| email | text | Source email; retained as supplied and not validated or used. |
| last_updated | text | Source update date; retained without parsing. |
| revenue | decimal EUR | Derived as `quantity × unit_price`, rounded/formatted to two decimals. |

## `revenue_by_category.csv`

| Column | Type | Meaning |
|---|---|---|
| category | text | Category from accepted orders, sorted alphabetically. |
| order_count | integer | Number of accepted order rows in the category. |
| revenue_eur | decimal EUR | Sum of row revenue in EUR, formatted to two decimals. |

## `rejected_orders.csv` addition

`rejection_reason` records the first validation rule that rejects a source row. A row is preserved in full otherwise, so it can be corrected upstream and reprocessed.
