# Cleaning log

| Change | Why | Treatment |
|---|---|---|
| Parse three observed date formats and write ISO dates | March export mixes ISO, dotted, and slash-formatted dates | Normalize accepted `order_date`; quarantine malformed/future values. |
| Trim whitespace from all source fields | Avoid avoidable key and category inconsistencies | Applied in memory; raw input remains unchanged. |
| Reject duplicate order IDs | Duplicate order rows would inflate revenue | First occurrence is considered; subsequent occurrences are quarantined. |
| Reject quantity outside 1–100 | Negative/zero units are invalid; 500 is implausible for this exercise | Quarantine with explicit reason; threshold is an exercise rule, not a general business fact. |
| Reject missing or negative unit price | Revenue cannot be calculated reliably | Quarantine; do not impute. |
| Normalize `€` to EUR and reject other currencies | No foreign-exchange rates or conversion date were provided | EUR-only aggregate; preserve excluded rows in quarantine. |
| Require a category | Category output would otherwise be incomplete | Quarantine missing category; preserve unrecognized nonblank category labels. |
| Add `revenue` | Enables the requested new aggregate | Calculate quantity × unit price with decimal arithmetic. |

The validator stops at the first rejection reason per row. Accepted rows may still contain incomplete optional fields such as email or customer name; no speculative imputation is performed.
