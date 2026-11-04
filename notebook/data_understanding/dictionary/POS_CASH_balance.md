# POS_CASH_balance — Data Dictionary

> Monthly balance snapshots of previous POS (point of sales) and cash loans that the applicant had with Home Credit.
>
> This table has one row for each month of history of every previous credit in Home Credit (consumer credit and cash loans) related to loans in our sample – i.e. the table has (#loans in sample * # of relative previous credits * # of months in which we have some history observable for the previous credits) rows.

## Business Meaning

`POS_CASH_balance` captures the **monthly historical behavior of previous POS and cash loans** that an applicant had with Home Credit.

A row does **not** represent a loan or an applicant independently. Instead, each row represents the **monthly snapshot of one previous credit belonging to one applicant**.

The table therefore provides longitudinal behavioral information about previous credit accounts, including their repayment status, remaining installments, contract status, and delinquency.

## Column Definitions

| Column | Meaning |
|---|---|
| `SK_ID_PREV` | ID of a previous credit in Home Credit related to the current loan in our sample. One current loan (`SK_ID_CURR`) can have zero, one, or multiple previous credits. |
| `SK_ID_CURR` | ID of the current loan/application in our sample. This is the key used to associate historical POS/Cash loan records with the applicant in the application dataset. |
| `MONTHS_BALANCE` | Relative month of the monthly balance snapshot with respect to the current application date. `-1` represents the freshest monthly snapshot before the application; `0` represents information at the application date. |
| `CNT_INSTALMENT` | Number of installments specified for the previous credit at the given monthly snapshot. The contractual term may change over the lifetime of the credit. |
| `CNT_INSTALMENT_FUTURE` | Number of installments remaining to be paid on the previous credit at the given monthly snapshot. |
| `NAME_CONTRACT_STATUS` | Contract status of the previous credit during the given month, describing the state of the credit account at that point in its lifecycle. |
| `SK_DPD` | Days Past Due (DPD) of the previous credit during the given month. It measures the number of days by which the credit was overdue. |
| `SK_DPD_DEF` | Days Past Due under a tolerance-based definition, where debts with sufficiently low loan amounts are ignored. This represents delinquency after applying the business-specific tolerance rule. |

## Business Interpretation

The table can be understood hierarchically:

`SK_ID_CURR` → `SK_ID_PREV` → `MONTHS_BALANCE`

That is:

- One current application/customer can have multiple previous credits.
- One previous credit can have multiple monthly snapshots.
- Each monthly snapshot contains the behavioral state of that credit at that point in time.

Therefore, `POS_CASH_balance` is fundamentally a **longitudinal credit-behavior table**, rather than a simple customer-level feature table.

## Credit Risk Relevance

The table can be used to derive behavioral features such as:

- Maximum DPD over a historical period.
- Number of months with delinquency.
- Number of previous credits with delinquency.
- Recent contract status.
- Number of active previous credits.
- Number of remaining installments.
- Historical repayment deterioration or improvement.

These raw monthly observations must generally be **aggregated to the applicant/application level** before being used in a credit scorecard.

**Source:** Home Credit Default Risk — Kaggle.