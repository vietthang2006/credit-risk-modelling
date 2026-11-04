# credit_card_balance.csv — Data Dictionary

> Monthly balance snapshots of previous credit cards that the applicant has with Home Credit.
>
> This table has one row for each month of history of every previous credit in Home Credit (consumer credit and cash loans) related to loans in our sample – i.e. the table has (#loans in sample * # of relative previous credit cards * # of months where we have some history observable for the previous credit card) rows.

## Business Meaning

The `credit_card_balance` table contains **monthly snapshots of previous credit card accounts that the applicant had with Home Credit**.

Each row represents the monthly state of one previous credit card associated with an applicant's current loan application.

The table captures several dimensions of credit card behavior over time, including:

- Credit exposure and utilization.
- Credit card spending and cash withdrawals.
- Payment and repayment behavior.
- Outstanding receivables.
- Account lifecycle and maturity.
- Delinquency.

The relationship can be represented as:

`SK_ID_CURR → SK_ID_PREV → MONTHS_BALANCE`

This means that one current loan application can be associated with multiple previous credit cards, and each previous credit card can have multiple monthly balance observations.

## Column Groups

Because `credit_card_balance` contains many variables describing different aspects of credit card behavior, the columns are grouped by their **business meaning** rather than listed as one undifferentiated set.

### 1. Identification and Time

These columns identify the applicant, the previous credit card account, and the monthly observation point.

| Column | Meaning |
|---|---|
| `SK_ID_PREV` | ID of a previous credit in Home Credit related to the current loan application. One current loan can have zero, one, or multiple previous credits. |
| `SK_ID_CURR` | ID of the current loan/application in our sample. |
| `MONTHS_BALANCE` | Relative month of the balance snapshot with respect to the current application date. `-1` represents the freshest available balance snapshot before the application date. |

### 2. Credit Exposure and Utilization

These columns describe how much credit the applicant has outstanding and how much of the available credit limit is being used.

| Column | Meaning |
|---|---|
| `AMT_BALANCE` | Outstanding balance on the previous credit card during the month. |
| `AMT_CREDIT_LIMIT_ACTUAL` | Actual credit card limit during the month. |

The two variables can be combined to derive a credit utilization measure:

`Credit Utilization = AMT_BALANCE / AMT_CREDIT_LIMIT_ACTUAL`

A persistently high utilization can indicate that the applicant is relying heavily on available revolving credit.

### 3. Credit Card Drawings and Spending

These columns describe how the applicant used the credit card during the month.

| Column | Meaning |
|---|---|
| `AMT_DRAWINGS_ATM_CURRENT` | Amount withdrawn from ATMs using the credit card during the month. |
| `AMT_DRAWINGS_CURRENT` | Total amount of credit card drawings during the month. |
| `AMT_DRAWINGS_OTHER_CURRENT` | Amount of other types of credit card drawings during the month, excluding ATM and POS drawings. |
| `AMT_DRAWINGS_POS_CURRENT` | Amount spent on goods or services through POS transactions during the month. |
| `CNT_DRAWINGS_ATM_CURRENT` | Number of ATM withdrawals during the month. |
| `CNT_DRAWINGS_CURRENT` | Total number of credit card drawings during the month. |
| `CNT_DRAWINGS_OTHER_CURRENT` | Number of other credit card drawings during the month. |
| `CNT_DRAWINGS_POS_CURRENT` | Number of POS purchases during the month. |

The `AMT_*` variables measure **monetary volume**, while the corresponding `CNT_*` variables measure **transaction frequency**.

For example:

- High `AMT_DRAWINGS_POS_CURRENT` → high purchase volume.
- High `CNT_DRAWINGS_POS_CURRENT` → frequent POS usage.
- High `AMT_DRAWINGS_ATM_CURRENT` → substantial cash withdrawal activity.

These provide behavioral information about how the applicant uses revolving credit.

### 4. Payment and Repayment Behavior

These columns describe the applicant's payment obligations and actual payments.

| Column | Meaning |
|---|---|
| `AMT_INST_MIN_REGULARITY` | Minimum installment/payment amount required for the month. |
| `AMT_PAYMENT_CURRENT` | Amount paid by the client during the month on the previous credit card. |
| `AMT_PAYMENT_TOTAL_CURRENT` | Total amount paid by the client during the month on the previous credit card. |

These variables allow comparison between **payment obligations and actual repayment behavior**.

For example, a persistent pattern where actual payments are low relative to the required or outstanding amount may indicate weaker repayment capacity.

### 5. Outstanding Receivables

These columns describe the amounts that remain receivable from the applicant.

| Column | Meaning |
|---|---|
| `AMT_RECEIVABLE_PRINCIPAL` | Principal amount still receivable on the previous credit card. |
| `AMT_RECIVABLE` | Amount receivable on the previous credit card. |
| `AMT_TOTAL_RECEIVABLE` | Total amount receivable on the previous credit card. |

These variables represent the applicant's **outstanding financial obligation** associated with the previous credit card.

### 6. Account Lifecycle and Installment Progress

These columns describe the status and progression of the previous credit card account.

| Column | Meaning |
|---|---|
| `CNT_INSTALMENT_MATURE_CUM` | Cumulative number of installments that have matured on the previous credit card. |
| `NAME_CONTRACT_STATUS` | Contract status of the previous credit card during the month, such as active or signed. |

These variables provide information about the **lifecycle and maturity progression** of the credit account.

### 7. Delinquency and Credit Risk

These columns describe whether and to what extent the applicant was past due.

| Column | Meaning |
|---|---|
| `SK_DPD` | Days Past Due (DPD) during the month on the previous credit card. |
| `SK_DPD_DEF` | Days Past Due under a tolerance-based definition, where debts with low loan amounts are ignored. |

`SK_DPD` measures the observed delinquency, while `SK_DPD_DEF` applies the business-specific tolerance rule.

Higher DPD generally represents more severe repayment problems.

## Credit Risk Relevance

The table provides information about how the applicant actually **used and repaid revolving credit** before the current application.

Important behavioral dimensions include:

- **Utilization:** How much of the available credit limit was being used.
- **Spending behavior:** How much and how frequently the applicant used the credit card.
- **Cash withdrawal behavior:** How much and how frequently the applicant withdrew cash.
- **Repayment behavior:** How much the applicant paid relative to their obligations.
- **Outstanding exposure:** How much debt and receivables remained.
- **Delinquency:** Whether the applicant had payment delays and how severe they were.
- **Account progression:** How the previous credit card evolved over time.

Because each applicant can have multiple previous credit cards and each card can have multiple monthly observations, the raw data generally needs to be **aggregated before modeling**.

### Examples of Potential Application-Level Features

After aggregating the monthly observations and previous credit cards to the application level, potential features include:

- Maximum credit utilization over the observation window.
- Average credit utilization.
- Maximum DPD.
- Number of months with DPD.
- Number of delinquent previous credit cards.
- Total payment amount.
- Payment-to-balance ratio.
- Total drawing amount.
- ATM withdrawal frequency.
- POS purchase frequency.
- Average outstanding balance.
- Number of active previous credit cards.

These features convert the monthly credit card history into **applicant-level behavioral risk characteristics** that can be used by the credit scorecard.

**Source:** Home Credit Default Risk — Kaggle.
