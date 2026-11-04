# bureau.csv — Data Dictionary

> All client's previous credits provided by other financial institutions that were reported to Credit Bureau (for clients who have a loan in our sample).
>
> For every loan in our sample, there are as many rows as number of credits the client had in Credit Bureau before the application date.

## Business Meaning

The `bureau` table contains the applicant's **previous credit accounts provided by other financial institutions** and reported to the Credit Bureau.

A row represents **one previous credit account associated with an applicant's current loan application**. Therefore, one `SK_ID_CURR` can be associated with zero, one, or multiple `SK_BUREAU_ID` records.

Unlike `previous_application`, which contains previous applications made at Home Credit, `bureau` represents **external credit history** obtained from the Credit Bureau.

## Column Definitions

| Column | Meaning |
|---|---|
| `SK_ID_CURR` | ID of the current loan/application in our sample. It links the Credit Bureau records to the applicant's current loan application. |
| `SK_BUREAU_ID` | Recoded ID of a previous Credit Bureau credit related to the current loan application. It uniquely identifies a previous credit account for the application. |
| `CREDIT_ACTIVE` | Status of the Credit Bureau reported credit, indicating the current state of the credit account. |
| `CREDIT_CURRENCY` | Recoded currency of the Credit Bureau credit. |
| `DAYS_CREDIT` | Number of days before the current application when the client applied for or obtained the Credit Bureau credit. It describes the recency of the previous credit. |
| `CREDIT_DAY_OVERDUE` | Number of days the Credit Bureau credit was past due at the time of the current loan application. |
| `DAYS_CREDIT_ENDDATE` | Remaining duration of the Credit Bureau credit, expressed in days, at the time of the current application. |
| `DAYS_ENDDATE_FACT` | Number of days since the Credit Bureau credit actually ended, measured at the time of the current application. This applies only to closed credits. |
| `AMT_CREDIT_MAX_OVERDUE` | Maximum amount that had been overdue on the Credit Bureau credit up to the current application date. |
| `CNT_CREDIT_PROLONG` | Number of times the Credit Bureau credit was prolonged or extended. |
| `AMT_CREDIT_SUM` | Current credit amount associated with the Credit Bureau credit. |
| `AMT_CREDIT_SUM_DEBT` | Current outstanding debt on the Credit Bureau credit. |
| `AMT_CREDIT_SUM_LIMIT` | Current credit limit of a credit card reported by the Credit Bureau. |
| `AMT_CREDIT_SUM_OVERDUE` | Current amount overdue on the Credit Bureau credit. |
| `CREDIT_TYPE` | Type of Credit Bureau credit, such as consumer credit, cash loan, car loan, or credit card. |
| `DAYS_CREDIT_UPDATE` | Number of days before the current loan application when information about the Credit Bureau credit was last updated. |
| `AMT_ANNUITY` | Annuity, or periodic repayment amount, associated with the Credit Bureau credit. |

## Business Interpretation

The table can be understood as:

`SK_ID_CURR` → `SK_BUREAU_ID`

One current loan application can have multiple previous credit accounts reported by the Credit Bureau.

The variables describe four main aspects of the applicant's external credit history:

1. **Credit account characteristics**
   - `CREDIT_ACTIVE`
   - `CREDIT_CURRENCY`
   - `CREDIT_TYPE`

2. **Credit exposure and debt**
   - `AMT_CREDIT_SUM`
   - `AMT_CREDIT_SUM_DEBT`
   - `AMT_CREDIT_SUM_LIMIT`
   - `AMT_ANNUITY`

3. **Delinquency and repayment problems**
   - `CREDIT_DAY_OVERDUE`
   - `AMT_CREDIT_MAX_OVERDUE`
   - `AMT_CREDIT_SUM_OVERDUE`
   - `CNT_CREDIT_PROLONG`

4. **Credit history timing**
   - `DAYS_CREDIT`
   - `DAYS_CREDIT_ENDDATE`
   - `DAYS_ENDDATE_FACT`
   - `DAYS_CREDIT_UPDATE`

## Credit Risk Relevance

The `bureau` table provides **external credit history** that can be used to assess an applicant's existing indebtedness, previous delinquency, credit exposure, and overall credit behavior.

Because multiple Credit Bureau records can belong to the same applicant, the raw table generally needs to be **aggregated to the application/customer level** before being used as model features.

Examples of derived features include:

- Number of previous Credit Bureau accounts.
- Number of active credits.
- Number of closed credits.
- Maximum days overdue.
- Total outstanding debt.
- Total credit exposure.
- Total overdue amount.
- Number of credits with overdue balances.
- Number of credit prolongations.
- Recency of the most recent previous credit.

**Source:** Home Credit Default Risk — Kaggle.