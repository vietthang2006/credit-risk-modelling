# previous_application.csv — Data Dictionary

> Historical credit application records of the applicant with Home Credit.
>
> This table contains one row for each previous credit application related to loans in our sample. A current loan can be associated with zero, one, or multiple previous applications, and a previous application does not necessarily result in an approved credit.

## Business Meaning

The `previous_application` table contains **historical credit application records of applicants who had previous interactions with Home Credit**.

Each row represents one previous credit application and records information about:

* The type and purpose of the previous credit application.
* The amount requested and the amount of credit eventually granted.
* The down payment, annuity, and repayment term.
* The result of the previous application.
* The reason for rejection when the application was refused.
* The product, channel, seller, and customer characteristics associated with the application.
* The timing and lifecycle of the previous credit.

The table therefore provides information about the applicant's **historical credit-seeking behavior, previous underwriting outcomes, product usage, and historical credit characteristics**.

The relationship can be represented as:

`SK_ID_CURR → SK_ID_PREV`

This means that one current loan application can be associated with zero, one, or multiple previous credit applications.

A previous credit application can subsequently have installment-level repayment records in `installments_payments.csv`, and may also be associated with historical account information in tables such as `POS_CASH_balance.csv` or `credit_card_balance.csv`.

## Column Groups

The columns are grouped according to their **business meaning** rather than treated as one undifferentiated set.

### 1. Identification

These columns identify the previous credit application and connect it to the current loan application.

| Column       | Meaning                                                                                                                                                     |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `SK_ID_PREV` | ID of a previous credit in Home Credit related to the current loan application. One current loan can be associated with zero, one, or multiple previous credits. |
| `SK_ID_CURR` | ID of the current loan/application in our sample.                                                                                                           |

`SK_ID_PREV` identifies a specific historical credit application, while `SK_ID_CURR` connects the historical application back to the current application.

The relationship is therefore:

`SK_ID_CURR → SK_ID_PREV`

where one `SK_ID_CURR` can have multiple `SK_ID_PREV` records.

### 2. Credit Amount and Financial Terms

These columns describe the amount requested, the amount granted, and the financial structure of the previous application.

| Column               | Meaning                                                                                                                                    |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `AMT_ANNUITY`        | Annuity amount of the previous application.                                                                                                |
| `AMT_APPLICATION`    | Amount of credit that the applicant requested on the previous application.                                                                |
| `AMT_CREDIT`         | Final credit amount granted on the previous application. This may differ from the amount initially requested by the applicant.            |
| `AMT_DOWN_PAYMENT`   | Down payment amount associated with the previous application.                                                                              |
| `AMT_GOODS_PRICE`    | Price of the goods that the applicant requested to purchase, when applicable.                                                             |
| `RATE_DOWN_PAYMENT`  | Normalized down payment rate of the previous credit.                                                                                       |
| `RATE_INTEREST_PRIMARY` | Normalized primary interest rate of the previous credit.                                                                                |
| `RATE_INTEREST_PRIVILEGED` | Normalized privileged or preferential interest rate of the previous credit.                                                           |

`AMT_APPLICATION` represents the applicant's initial credit demand, while `AMT_CREDIT` represents the amount actually granted after the Home Credit approval process.

The difference between the requested and granted amounts can therefore provide information about the previous underwriting decision.

A derived ratio can be calculated as:

`CREDIT_TO_APPLICATION_RATIO = AMT_CREDIT / AMT_APPLICATION`

This measures the proportion of the requested amount that was eventually granted.

When calculating this ratio, cases where `AMT_APPLICATION = 0` need to be handled separately.

### 3. Contract and Product Type

These columns describe the type, portfolio, and purpose of the previous credit product.

| Column                    | Meaning                                                                                       |
| ------------------------- | --------------------------------------------------------------------------------------------- |
| `NAME_CONTRACT_TYPE`      | Type of contract/product of the previous application, such as Cash loan or Consumer loan.   |
| `NAME_CASH_LOAN_PURPOSE`  | Purpose of the previous cash loan application.                                                |
| `NAME_GOODS_CATEGORY`     | Category of goods for which the applicant applied, when applicable.                          |
| `NAME_PORTFOLIO`          | Portfolio of the previous application, such as CASH, POS, or CAR.                            |
| `NAME_PRODUCT_TYPE`       | Type of previous product, such as `x-sell` or `walk-in`.                                     |
| `PRODUCT_COMBINATION`     | Detailed product combination associated with the previous application.                       |

These variables describe **what type of credit the applicant was seeking and how the credit product was structured**.

They can be used to distinguish different types of historical credit relationships and to measure the diversity of products previously used by the applicant.

### 4. Previous Application Outcome

These columns describe the result of the previous application and, when applicable, the reason for rejection.

| Column                  | Meaning                                                                                         |
| ----------------------- | ----------------------------------------------------------------------------------------------- |
| `NAME_CONTRACT_STATUS`  | Status of the previous application, such as Approved, Refused, Cancelled, or other statuses.  |
| `CODE_REJECT_REASON`    | Reason code explaining why the previous application was rejected, when applicable.             |

`NAME_CONTRACT_STATUS` is one of the most important variables in this table because it records the historical underwriting outcome.

For example:

* `Approved` → the previous application was approved.
* `Refused` → the previous application was rejected.
* `Cancelled` → the previous application was cancelled.
* `Unused offer` → the approved offer was not used.

The historical outcome can be aggregated at the `SK_ID_CURR` level to construct features such as:

`PREV_APPROVED_COUNT`

`PREV_REFUSED_COUNT`

`PREV_APPROVED_RATE`

`PREV_REFUSED_RATE`

These features describe the applicant's historical interaction with the credit approval process.

### 5. Application Timing

These columns describe when the previous application and related credit decisions occurred relative to the current application.

| Column                       | Meaning                                                                                                                               |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `WEEKDAY_APPR_PROCESS_START` | Day of the week on which the previous application was submitted.                                                                     |
| `HOUR_APPR_PROCESS_START`    | Approximate hour at which the previous application was submitted.                                                                     |
| `DAYS_DECISION`              | Number of days relative to the current application date when the decision on the previous application was made.                       |

`DAYS_DECISION` is particularly useful for measuring **recency of previous credit applications**.

For example, a previous application with a smaller absolute value of `DAYS_DECISION` represents a more recent historical credit event.

The timing information can therefore be used to construct features such as:

* Number of previous applications within the last 6 months.
* Number of previous applications within the last 12 months.
* Time since the most recent previous application.
* Average time between previous applications.

These features can capture the applicant's recent **credit-seeking behavior**.

### 6. Previous Credit Lifecycle

These columns describe important events in the lifecycle of the previous credit.

| Column                         | Meaning                                                                                                                    |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------------------- |
| `DAYS_FIRST_DRAWING`           | Number of days relative to the current application date when the first disbursement of the previous application occurred. |
| `DAYS_FIRST_DUE`               | Number of days relative to the current application date when the first payment was supposed to be due.                   |
| `DAYS_LAST_DUE_1ST_VERSION`    | Number of days relative to the current application date when the first-version final due date occurred.                  |
| `DAYS_LAST_DUE`                | Number of days relative to the current application date when the final due date occurred.                                 |
| `DAYS_TERMINATION`             | Number of days relative to the current application date when the expected termination of the previous credit occurred.  |

These variables describe the temporal structure of the previous credit:

`Application → Decision → Drawing → First Due → Last Due → Termination`

They can provide information about the duration and lifecycle of previous credit relationships.

### 7. Repayment Terms

These columns describe the expected repayment structure of the previous credit.

| Column         | Meaning                                                                                          |
| -------------- | ------------------------------------------------------------------------------------------------ |
| `CNT_PAYMENT`  | Number of installments or repayment periods specified when the previous credit was applied for. |

`CNT_PAYMENT` can be interpreted as the **repayment term** of the previous credit.

When combined with `AMT_CREDIT` and `AMT_ANNUITY`, it provides information about the structure of the historical repayment obligation.

Potential derived measures include:

`ANNUITY_TO_CREDIT = AMT_ANNUITY / AMT_CREDIT`

and aggregated statistics such as:

* Average previous credit term.
* Maximum previous credit term.
* Average previous annuity.
* Average annuity-to-credit ratio.

### 8. Customer and Application Context

These columns describe the customer context and circumstances surrounding the previous application.

| Column              | Meaning                                                                                       |
| ------------------- | --------------------------------------------------------------------------------------------- |
| `NAME_CLIENT_TYPE`  | Type of client at the time of the previous application, such as new or existing/repeater client. |
| `NAME_TYPE_SUITE`   | Person who accompanied the applicant when applying for the previous credit.                  |
| `NAME_PAYMENT_TYPE` | Payment method selected by the applicant for the previous credit.                            |

`NAME_CLIENT_TYPE` provides information about the applicant's relationship with Home Credit at the time of the previous application.

For example, a `Repeater` client indicates that the applicant already had a previous relationship with Home Credit.

These variables can therefore contribute to features describing **customer relationship history and application context**.

### 9. Sales Channel and Seller Information

These columns describe how and where the previous credit application was acquired.

| Column               | Meaning                                                                                         |
| -------------------- | ----------------------------------------------------------------------------------------------- |
| `CHANNEL_TYPE`       | Channel through which the applicant was acquired for the previous application.                  |
| `SELLERPLACE_AREA`   | Selling area of the seller associated with the previous application.                            |
| `NAME_SELLER_INDUSTRY` | Industry of the seller associated with the previous application.                              |

These variables provide information about the **distribution and merchant context** of historical credit applications.

They can be used to analyze whether applicants have historically used particular sales channels, seller industries, or selling areas.

### 10. Operational and Process Flags

These columns describe operational characteristics of the previous application.

| Column                    | Meaning                                                                                                                        |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `FLAG_LAST_APPL_PER_CONTRACT` | Flag indicating whether the application was the last application for the previous contract.                                |
| `NFLAG_LAST_APPL_IN_DAY`      | Flag indicating whether the application was the last application submitted by the client on that day.                       |
| `NFLAG_INSURED_ON_APPROVAL`   | Flag indicating whether the applicant requested insurance when the previous application was approved.                        |

`FLAG_LAST_APPL_PER_CONTRACT` and `NFLAG_LAST_APPL_IN_DAY` are primarily related to the application process and data recording behavior.

They can be useful for identifying repeated applications or duplicate application activity, but should not automatically be interpreted as direct measures of credit risk.

`NFLAG_MICRO_CASH` and `NFLAG_INSURED_ON_APPROVAL` describe specific product and customer choices associated with the previous application.

## Credit Risk Relevance

The `previous_application` table provides information about the applicant's **historical credit-seeking behavior and previous underwriting outcomes**.

Important dimensions include:

* **Historical application volume:** How many times the applicant previously applied for credit.
* **Approval history:** How frequently previous applications were approved.
* **Rejection history:** How frequently previous applications were refused.
* **Credit demand:** How much credit the applicant historically requested.
* **Granted credit:** How much credit was actually granted.
* **Credit structure:** Historical annuity, down payment, and repayment term.
* **Credit recency:** How recently the applicant interacted with Home Credit.
* **Product behavior:** Which types of credit products the applicant historically requested.
* **Channel behavior:** Which channels and seller industries were associated with previous applications.
* **Customer relationship:** Whether the applicant was a new or returning customer.

The table therefore provides historical context that can complement the applicant's current financial and demographic information.

However, `previous_application` primarily describes **application and underwriting history**. It does not by itself provide complete information about whether the applicant actually repaid previous obligations on time. Detailed repayment behavior should be obtained from tables such as `installments_payments.csv`, `POS_CASH_balance.csv`, and `credit_card_balance.csv`.

## Relationship to Other Tables

The table is connected to the current application through `SK_ID_CURR` and to historical credit-level records through `SK_ID_PREV`.

The main relationships can be represented as:

`previous_application.csv → SK_ID_CURR → application_train.csv / application_test.csv`

`previous_application.csv → SK_ID_PREV → installments_payments.csv`

`previous_application.csv → SK_ID_PREV → POS_CASH_balance.csv`

`previous_application.csv → SK_ID_PREV → credit_card_balance.csv`

Conceptually:

`current application`
→ `previous applications`
→ `historical credit accounts`
→ `repayment / account behavior`

The relationship between `SK_ID_CURR` and `SK_ID_PREV` is one-to-many:

`1 SK_ID_CURR → N SK_ID_PREV`

This means that a single current application can have multiple previous credit applications.

The relationship between `SK_ID_PREV` and installment-level records is also one-to-many:

`1 SK_ID_PREV → N installment records`

Therefore, the previous application table acts as an intermediate historical-credit layer between the current application and detailed historical repayment/account tables.

## Aggregation for Credit Scorecard

The raw table is at the **previous-application level**, while the target variable in the Home Credit Default Risk problem is defined at the **current application level**.

Therefore, previous applications should generally be aggregated to the `SK_ID_CURR` level before being combined with the current application dataset.

Directly joining the raw table to the application table can create multiple rows for a single current application because one `SK_ID_CURR` may have multiple previous applications.

The typical transformation is:

`previous_application`

→ `groupby(SK_ID_CURR)`

→ `aggregate historical application behavior`

→ `one row per SK_ID_CURR`

### Examples of Potential Application-Level Features

After aggregation, potential features include:

* Number of previous applications.
* Number of approved previous applications.
* Number of refused previous applications.
* Number of cancelled previous applications.
* Approval rate.
* Refusal rate.
* Average previous application amount.
* Maximum previous application amount.
* Average previous credit amount.
* Maximum previous credit amount.
* Total previous credit amount.
* Average credit-to-application ratio.
* Average down payment.
* Average annuity.
* Average previous credit term.
* Average annuity-to-credit ratio.
* Number of recent previous applications.
* Time since the most recent previous application.
* Number of unique previous contract types.
* Number of unique previous portfolios.
* Number of unique goods categories.
* Number of unique channels.
* Proportion of `x-sell` applications.
* Proportion of applications associated with high yield groups.

These features convert the historical application records into **application-level historical credit characteristics** that can be incorporated into the credit scorecard.

## Example Feature Interpretation

For example, consider two applicants with similar current financial characteristics.

Applicant A has:

* Many previous applications.
* A high historical approval rate.
* A low historical refusal rate.
* Relatively stable previous credit amounts.
* Several previous credits successfully reaching later repayment stages.

Applicant B has:

* Many previous applications.
* A low historical approval rate.
* A high historical refusal rate.
* Frequent differences between requested and granted credit amounts.
* Several recent refused applications.

The two applicants have different historical interactions with the credit approval process.

Features derived from `previous_application` can therefore capture information that is not visible from the current application alone.

However, historical application outcomes should not be interpreted as direct proof of repayment ability. A previous application being approved does not necessarily mean that the corresponding credit was repaid successfully. Repayment behavior should be analyzed using the related historical payment and account tables.

## Key Derived Variables

### Previous Application Count

`PREV_COUNT = COUNT(SK_ID_PREV)`

Measures the number of previous credit applications associated with the current application.

### Approval Rate

`PREV_APPROVED_RATE = PREV_APPROVED_COUNT / PREV_COUNT`

Measures the proportion of previous applications that were approved.

### Refusal Rate

`PREV_REFUSED_RATE = PREV_REFUSED_COUNT / PREV_COUNT`

Measures the proportion of previous applications that were refused.

### Credit-to-Application Ratio

`CREDIT_TO_APPLICATION_RATIO = AMT_CREDIT / AMT_APPLICATION`

Measures the proportion of the requested credit amount that was eventually granted.

### Annuity-to-Credit Ratio

`ANNUITY_TO_CREDIT = AMT_ANNUITY / AMT_CREDIT`

Measures the size of the historical annuity relative to the granted credit amount.

### Previous Application Recency

`PREV_RECENT_DAYS = MIN(ABS(DAYS_DECISION))`

Measures the approximate time distance between the current application and the most recent previous application.

### Recent Application Count

`PREV_APPLICATIONS_LAST_6M`

Number of previous applications whose decision occurred within the six months preceding the current application.

This feature can capture recent credit-seeking behavior.

## Role in the Credit Scorecard Project

`previous_application.csv` is one of the most important sources of **historical credit application features** in the Home Credit dataset.

While the `application` tables describe the applicant's current financial, demographic, and employment characteristics, `previous_application` describes **how the applicant interacted with Home Credit in the past**.

Its primary contribution to the scorecard is therefore the construction of features that answer questions such as:

* How many times has the applicant previously applied for credit?
* How frequently were previous applications approved or refused?
* How much credit did the applicant historically request?
* How much credit was historically granted?
* How recently has the applicant sought credit?
* Which credit products has the applicant previously used?
* How large were previous repayment obligations?
* Does the applicant have a long-standing relationship with Home Credit?

The table should be interpreted together with historical repayment tables.

`previous_application` describes **what the applicant applied for and what happened during the application process**, while `installments_payments`, `POS_CASH_balance`, and `credit_card_balance` provide evidence about **what happened after credit was granted**.

The combined relationship can therefore be represented as:

`Current application`

→ `Previous applications`

→ `Historical credit accounts`

→ `Historical repayment behavior`

This hierarchy allows the credit scorecard to combine current applicant characteristics, historical credit application behavior, and observed repayment behavior when estimating the probability of payment difficulties on the current loan.

**Source:** Home Credit Default Risk — Kaggle.