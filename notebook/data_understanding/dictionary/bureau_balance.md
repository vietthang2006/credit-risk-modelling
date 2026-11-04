# bureau_balance.csv — Data Dictionary

> Monthly balances of previous credits in Credit Bureau.
>
> This table has one row for each month of history of every previous credit reported to Credit Bureau – i.e the table has (#loans in sample * # of relative previous credits * # of months where we have some history observable for the previous credits) rows.

## Business Meaning

The `bureau_balance` table contains the **monthly historical status of previous credit accounts reported to the Credit Bureau**.

While the `bureau` table describes the characteristics and current state of each previous credit account, `bureau_balance` provides its **longitudinal monthly history**.

Each row represents the status of **one Credit Bureau credit (`SK_BUREAU_ID`) in one relative month (`MONTHS_BALANCE`)**.

The relationship can be represented as:

`SK_ID_CURR → SK_BUREAU_ID → MONTHS_BALANCE`

This means that one current loan application can be associated with multiple previous Credit Bureau credits, and each previous credit can have multiple monthly balance observations.

## Column Definitions

| Column | Meaning |
|---|---|
| `SK_BUREAU_ID` | Recoded ID of a previous Credit Bureau credit. It uniquely identifies the Credit Bureau credit and is used to join `bureau_balance` with the `bureau` table. |
| `MONTHS_BALANCE` | Relative month of the monthly balance snapshot with respect to the current loan application date. `-1` represents the freshest available balance snapshot before the application date. |
| `STATUS` | Status of the Credit Bureau credit during the given month. `C` means the credit was closed; `X` means the status is unknown; `0` means no days past due (DPD); `1` means the maximum DPD during the month was 1–30 days; `2` means 31–60 days; higher values represent increasingly severe delinquency, with `5` representing DPD 120+ or a credit that was sold or written off. |

## STATUS Interpretation

| STATUS | Credit Risk Interpretation |
|---|---|
| `C` | Credit was closed during the observed period. |
| `X` | Credit status is unknown. |
| `0` | No delinquency was reported during the month. |
| `1` | Maximum DPD during the month was 1–30 days. |
| `2` | Maximum DPD during the month was 31–60 days. |
| `3` | Maximum DPD during the month was 61–90 days. |
| `4` | Maximum DPD during the month was 91–120 days. |
| `5` | DPD was 120+ days, or the credit was sold or written off. |

## Business Interpretation

The `bureau_balance` table represents the **longitudinal repayment behavior of external credit accounts**.

The `bureau` table answers:

> What previous credits does the applicant have in the Credit Bureau?

The `bureau_balance` table answers:

> How did each of those credits behave month by month?

For example, a single `SK_BUREAU_ID` may have the following history:

| `MONTHS_BALANCE` | `STATUS` |
|---:|---:|
| -12 | 0 |
| -11 | 0 |
| -10 | 1 |
| -9 | 2 |
| -8 | 1 |
| -7 | 0 |
| ... | ... |
| -1 | 0 |

This indicates that the credit account was initially performing normally, experienced delinquency during the historical period, and subsequently returned to a non-delinquent status.

## Credit Risk Relevance

`bureau_balance` provides behavioral information that is not available from a single snapshot in `bureau`.

It can be aggregated to derive application-level features such as:

- Maximum historical delinquency status.
- Number of months with delinquency.
- Number of months with severe delinquency.
- Number of previous credits that experienced delinquency.
- Most recent delinquency status.
- Recency of the most recent delinquency.
- Frequency of delinquency over a defined historical window.

Because one applicant can have multiple Credit Bureau credits and each credit can have multiple monthly observations, the raw table must generally be aggregated before being used for modeling.

**Source:** Home Credit Default Risk - Kaggle
