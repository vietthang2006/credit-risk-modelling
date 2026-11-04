# installments_payments.csv — Data Dictionary

> Installment-level payment records of previous credits that the applicant has with Home Credit.
>
> This table contains one row for each installment payment of every previous credit related to loans in our sample. A current loan can be associated with zero, one, or multiple previous credits, and each previous credit can contain multiple installment records.

## Business Meaning

The `installments_payments` table contains **historical installment-level repayment records of previous credits that the applicant had with Home Credit**.

Each row represents one installment of a previous credit and records both:

* When the installment was **supposed to be paid**.
* When the installment was **actually paid**.
* How much the applicant was **supposed to pay**.
* How much the applicant **actually paid**.

The table therefore provides direct information about the applicant's **historical repayment behavior**, rather than only static characteristics of the previous credit.

The relationship can be represented as:

`SK_ID_CURR → SK_ID_PREV → NUM_INSTALMENT_NUMBER`

This means that one current loan application can be associated with multiple previous credits, and each previous credit can contain multiple installment observations.

## Column Groups

The columns are grouped according to their **business meaning** rather than treated as one undifferentiated set.

### 1. Identification

These columns identify the current loan application and the previous credit associated with the installment record.

| Column       | Meaning                                                                                                                                                          |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `SK_ID_PREV` | ID of a previous credit in Home Credit related to the current loan application. One current loan can be associated with zero, one, or multiple previous credits. |
| `SK_ID_CURR` | ID of the current loan/application in our sample.                                                                                                                |

`SK_ID_PREV` identifies the historical credit account, while `SK_ID_CURR` connects the historical installment information back to the current application.

### 2. Installment Schedule

These columns describe the installment calendar and the position of the installment within the previous credit.

| Column                   | Meaning                                                                                                                                                                                                          |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `NUM_INSTALMENT_VERSION` | Version of the installment calendar of the previous credit. `0` is used for credit cards. A change in installment version from month to month indicates that some parameter of the payment calendar has changed. |
| `NUM_INSTALMENT_NUMBER`  | Sequential number of the installment on which the payment is observed.                                                                                                                                           |

`NUM_INSTALMENT_VERSION` can provide information about changes to the repayment schedule during the lifetime of the previous credit.

`NUM_INSTALMENT_NUMBER` indicates the position of the installment within the repayment schedule and can be useful when analyzing whether repayment problems occur at particular stages of the credit lifecycle.

### 3. Scheduled and Actual Payment Dates

These columns describe when the installment was expected to be paid and when the payment actually occurred.

| Column               | Meaning                                                                                               |
| -------------------- | ----------------------------------------------------------------------------------------------------- |
| `DAYS_INSTALMENT`    | Number of days relative to the current application date when the installment was supposed to be paid. |
| `DAYS_ENTRY_PAYMENT` | Number of days relative to the current application date when the installment was actually paid.       |

The difference between these two variables can be used to measure **payment delay**:

`PAYMENT_DELAY = DAYS_ENTRY_PAYMENT - DAYS_INSTALMENT`

Interpretation:

* `PAYMENT_DELAY > 0` → payment was made after the scheduled date.
* `PAYMENT_DELAY = 0` → payment was made on the scheduled date.
* `PAYMENT_DELAY < 0` → payment was made before the scheduled date.

Payment delay is one of the most important behavioral indicators available in this table.

### 4. Scheduled and Actual Payment Amounts

These columns describe the amount that the applicant was expected to pay and the amount actually paid.

| Column           | Meaning                                                               |
| ---------------- | --------------------------------------------------------------------- |
| `AMT_INSTALMENT` | Prescribed installment amount that the applicant was expected to pay. |
| `AMT_PAYMENT`    | Amount that the applicant actually paid for the installment.          |

The two variables can be compared to measure **repayment completeness**.

A payment ratio can be derived as:

`PAYMENT_RATIO = AMT_PAYMENT / AMT_INSTALMENT`

Interpretation:

* `PAYMENT_RATIO ≈ 1` → approximately full payment.
* `PAYMENT_RATIO < 1` → partial payment.
* `PAYMENT_RATIO > 1` → payment exceeded the prescribed installment.

When calculating this ratio, cases where `AMT_INSTALMENT = 0` need to be handled separately.

An underpayment measure can also be derived:

`UNDERPAYMENT = AMT_INSTALMENT - AMT_PAYMENT`

A positive value indicates that the applicant paid less than the prescribed installment.

## Credit Risk Relevance

The table provides direct evidence of how the applicant **repaid previous credit obligations**.

Important behavioral dimensions include:

* **Payment timeliness:** Whether installments were paid before, on, or after their scheduled dates.
* **Delinquency:** How frequently and how severely the applicant made late payments.
* **Payment completeness:** Whether the applicant paid the full prescribed installment.
* **Repayment consistency:** Whether payment problems were isolated events or recurring patterns.
* **Historical repayment performance:** Whether the applicant demonstrated reliable repayment behavior across previous credits.
* **Payment schedule stability:** Whether the installment calendar changed during the previous credit.

This information is particularly valuable for credit risk modeling because past repayment behavior can provide evidence about the applicant's ability and willingness to meet future credit obligations.

## Relationship to Other Tables

The table can be connected to other Home Credit datasets through its two main identifiers:

`installments_payments.csv → SK_ID_PREV → previous credit information`

`installments_payments.csv → SK_ID_CURR → application_train.csv / application_test.csv`

Conceptually:

`installment records`
→ `previous credit`
→ `current application`

`SK_ID_PREV` is used to analyze repayment behavior within a specific previous credit, while `SK_ID_CURR` is used to aggregate historical repayment behavior for the current application.

## Aggregation for Credit Scorecard

The raw table is at the **installment level**, while the target variable in the Home Credit Default Risk problem is defined at the **application level**.

Therefore, the raw installment records generally should not be joined directly to the application dataset. Doing so would create multiple rows for a single application and introduce a one-to-many relationship.

Instead, installment-level information should be transformed into aggregated behavioral features at the `SK_ID_CURR` level.

### Examples of Potential Application-Level Features

After aggregating the installment records, potential features include:

* Average payment delay.
* Maximum payment delay.
* Minimum payment delay.
* Number of late payments.
* Proportion of late payments.
* Number of severely late payments.
* Average payment ratio.
* Minimum payment ratio.
* Proportion of partial payments.
* Total prescribed installment amount.
* Total actual payment amount.
* Total underpayment amount.
* Number of previous credits with late payments.
* Number of previous credits with repeated late payments.
* Number of previous credits with partial payments.
* Number of installment observations.
* Average number of days paid before or after the scheduled date.

These features convert the detailed installment history into **application-level behavioral risk characteristics** that can be incorporated into the credit scorecard.

## Example Feature Interpretation

For example, consider an applicant whose previous installment history shows:

* High average `PAYMENT_DELAY`.
* High maximum `PAYMENT_DELAY`.
* Large proportion of installments with `PAYMENT_DELAY > 0`.
* Low average `PAYMENT_RATIO`.
* Repeated underpayments across multiple previous credits.

This pattern indicates **persistent repayment difficulty**, which may be associated with a higher probability of payment difficulties on the current loan.

Conversely, an applicant with consistently low payment delays and payment ratios close to `1` demonstrates a stronger historical repayment profile.

The important point is that individual installment observations are less informative by themselves than the **aggregate behavioral pattern across the applicant's repayment history**.

## Key Derived Variables

### Payment Delay

`PAYMENT_DELAY = DAYS_ENTRY_PAYMENT - DAYS_INSTALMENT`

Measures how many days late or early the applicant paid relative to the scheduled installment date.

### Payment Ratio

`PAYMENT_RATIO = AMT_PAYMENT / AMT_INSTALMENT`

Measures the proportion of the prescribed installment that was actually paid.

### Underpayment

`UNDERPAYMENT = AMT_INSTALMENT - AMT_PAYMENT`

Measures the difference between the prescribed installment and the actual payment.

Positive values indicate that the applicant paid less than required.

## Role in the Credit Scorecard Project

`installments_payments.csv` is one of the most important sources of **behavioral features** in the Home Credit dataset.

While the `application` tables describe the applicant's current financial and demographic characteristics, `installments_payments` describes **observed historical repayment behavior**.

Its primary contribution to the scorecard is therefore the construction of features that answer questions such as:

* Does the applicant usually pay on time?
* How often does the applicant pay late?
* How severe are the applicant's payment delays?
* Does the applicant consistently pay the required amount?
* Does the applicant show repeated repayment problems across previous credits?

These behavioral features can complement static financial variables and previous-credit characteristics when estimating the applicant's probability of experiencing payment difficulties on the current loan.

**Source:** Home Credit Default Risk — Kaggle.
