# application_train.csv — Data Dictionary

> Application-level information about current loan applications in the Home Credit sample.
>
> This table contains one row for each current loan application and describes the applicant's demographic, financial, employment, housing, geographic, contact, external-score, social-circle, document, and credit-bureau-inquiry characteristics at the time of application.
>
> The target variable `TARGET` indicates whether the applicant experienced payment difficulties on the current loan.

## Business Meaning

The `application_train` table represents the **current loan application profile** of each applicant in the Home Credit sample.

Each row corresponds to one current loan application and contains information known around the time the application was submitted, including:

* The applicant's **financial capacity and requested credit**.
* The applicant's **demographic and family characteristics**.
* The applicant's **employment and occupational profile**.
* The applicant's **housing and property characteristics**.
* The applicant's **geographic and address consistency**.
* The applicant's **contact information and contactability**.
* Normalized scores from **external data sources**.
* Information about the applicant's **social surroundings**.
* Whether specific **documents were provided**.
* The number of recent **Credit Bureau enquiries**.

The relationship can be represented as:

`SK_ID_CURR → current loan application`

`SK_ID_CURR` is the key used to connect the current application to historical credit and repayment information in the other Home Credit tables.

The table therefore provides the **current application-level view** of the applicant, while tables such as `installments_payments`, `previous_application`, and `bureau` provide historical behavioral and credit information.

---

## Column Groups

The columns are grouped according to their **business meaning** rather than treated as one undifferentiated set.

### 1. Identification and Target

These columns identify the current loan application and define the modeling target.

| Column | Meaning |
| --- | --- |
| `SK_ID_CURR` | ID of the current loan/application in the sample. |
| `TARGET` | Target variable: `1` indicates a client with payment difficulties, while `0` indicates all other cases. |

`SK_ID_CURR` is used as the primary identifier and should not be used as a predictive feature.

`TARGET` is the dependent variable for the credit risk model and must not be included among the model predictors.

---

### 2. Loan and Application Characteristics

These columns describe the current credit product and the financial size of the application.

| Column | Meaning |
| --- | --- |
| `NAME_CONTRACT_TYPE` | Type of loan contract: cash loan or revolving loan. |
| `AMT_INCOME_TOTAL` | Total income of the client. |
| `AMT_CREDIT` | Amount of credit requested/granted for the current loan. |
| `AMT_ANNUITY` | Annuity amount of the current loan. |
| `AMT_GOODS_PRICE` | Price of the goods for which the loan is provided, applicable to consumer loans. |

These variables describe the relationship between the applicant's **financial capacity** and the **size and repayment burden of the requested credit**.

They are particularly useful for assessing affordability.

Potential derived measures include:

`CREDIT_INCOME = AMT_CREDIT / AMT_INCOME_TOTAL`

`ANNUITY_INCOME = AMT_ANNUITY / AMT_INCOME_TOTAL`

`GOODS_INCOME = AMT_GOODS_PRICE / AMT_INCOME_TOTAL`

`CREDIT_ANNUITY = AMT_CREDIT / AMT_ANNUITY`

These ratios provide relative measures of credit exposure and repayment burden rather than relying only on absolute monetary amounts.

When calculating ratios, zero or missing denominators must be handled separately.

---

### 3. Demographic and Family Characteristics

These columns describe the applicant's demographic, education, family, and household profile.

| Column | Meaning |
| --- | --- |
| `CODE_GENDER` | Gender of the client. |
| `CNT_CHILDREN` | Number of children the client has. |
| `NAME_TYPE_SUITE` | Person or group accompanying the client when applying for the loan. |
| `NAME_INCOME_TYPE` | Type of income or income source of the client, such as working, businessman, or maternity leave. |
| `NAME_EDUCATION_TYPE` | Highest level of education achieved by the client. |
| `NAME_FAMILY_STATUS` | Family or marital status of the client. |
| `NAME_HOUSING_TYPE` | Housing situation of the client, such as renting or living with parents. |
| `CNT_FAM_MEMBERS` | Number of family members of the client. |
| `FLAG_OWN_CAR` | Whether the client owns a car. |
| `FLAG_OWN_REALTY` | Whether the client owns a house or flat. |

These variables provide information about the applicant's **household structure, socioeconomic profile, and asset ownership**.

Potential derived variables include:

`HAS_CHILDREN = 1(CNT_CHILDREN > 0)`

`CHILDREN_PER_FAMILY = CNT_CHILDREN / CNT_FAM_MEMBERS`

Categorical variables can be handled using categorical encoding, WoE encoding, or appropriate grouping of rare categories.

---

### 4. Age, Employment, and Stability

These columns describe the applicant's age and the duration of several personal or administrative states before the current application.

| Column | Meaning |
| --- | --- |
| `DAYS_BIRTH` | Client's age expressed as the number of days before the application date. |
| `DAYS_EMPLOYED` | Number of days before the application when the client started their current employment. |
| `DAYS_REGISTRATION` | Number of days before the application when the client changed their registration. |
| `DAYS_ID_PUBLISH` | Number of days before the application when the client changed the identity document used for the application. |
| `OWN_CAR_AGE` | Age of the client's car. |

The `DAYS_*` variables are expressed relative to the application date and are generally negative.

For interpretability, age and employment duration can be transformed into years:

`AGE_YEARS = -DAYS_BIRTH / 365.25`

`EMPLOYMENT_YEARS = -DAYS_EMPLOYED / 365.25`

Potential additional features include:

* Age bands.
* Employment tenure bands.
* Recent identity-document change indicators.
* Car ownership and car-age combinations.

`DAYS_EMPLOYED` requires particular attention because anomalous values may exist and should be investigated separately rather than interpreted directly as valid employment duration.

---

### 5. Contactability

These columns indicate whether different contact channels were provided or whether the client could be reached.

| Column | Meaning |
| --- | --- |
| `FLAG_MOBIL` | Whether the client provided a mobile phone. |
| `FLAG_EMP_PHONE` | Whether the client provided a work phone. |
| `FLAG_WORK_PHONE` | Whether the client provided a home/work-related phone according to the dataset definition. |
| `FLAG_CONT_MOBILE` | Whether the client's mobile phone was reachable. |
| `FLAG_PHONE` | Whether the client provided a home phone. |
| `FLAG_EMAIL` | Whether the client provided an email address. |

These variables provide information about **contactability and communication channels**.

A potential aggregate feature is:

`CONTACT_COUNT = FLAG_MOBIL + FLAG_EMP_PHONE + FLAG_WORK_PHONE + FLAG_PHONE + FLAG_EMAIL`

Other possible derived variables include:

`NO_CONTACT_INFO`

and indicators for whether the applicant can be reached through multiple channels.

The individual flags should be examined for redundancy before all of them are included in a final scorecard.

---

### 6. Employment and Organization

These columns describe the applicant's occupation and the type of organization where they work.

| Column | Meaning |
| --- | --- |
| `OCCUPATION_TYPE` | Type of occupation of the client. |
| `ORGANIZATION_TYPE` | Type of organization where the client works. |

`OCCUPATION_TYPE` describes the applicant's occupation, while `ORGANIZATION_TYPE` describes the organization or sector in which the applicant works.

These variables can provide signals related to **employment stability and socioeconomic profile**.

Potential treatments include:

* Categorical encoding.
* WoE encoding.
* Rare-category grouping.
* Business-driven occupational or organizational grouping.

---

### 7. Geographic and Address Consistency

These columns describe the applicant's geographic region and whether registered, living, and work locations are consistent.

| Column | Meaning |
| --- | --- |
| `REGION_POPULATION_RELATIVE` | Normalized population of the region where the client lives. |
| `REGION_RATING_CLIENT` | Home Credit rating of the region where the client lives, taking values `1`, `2`, or `3`. |
| `REGION_RATING_CLIENT_W_CITY` | Home Credit rating of the region where the client lives, including city information. |
| `REG_REGION_NOT_LIVE_REGION` | Whether the client's permanent/registered address differs from the contact/living address at region level. |
| `REG_REGION_NOT_WORK_REGION` | Whether the client's permanent/registered address differs from the work address at region level. |
| `LIVE_REGION_NOT_WORK_REGION` | Whether the client's contact/living address differs from the work address at region level. |
| `REG_CITY_NOT_LIVE_CITY` | Whether the client's permanent/registered address differs from the contact/living address at city level. |
| `REG_CITY_NOT_WORK_CITY` | Whether the client's permanent/registered address differs from the work address at city level. |
| `LIVE_CITY_NOT_WORK_CITY` | Whether the client's contact/living address differs from the work address at city level. |

The address mismatch variables can provide signals related to **geographic mobility, residential stability, and consistency between personal and employment information**.

Potential aggregate features include:

`ADDRESS_MISMATCH_COUNT`

`REGION_MISMATCH_COUNT`

`CITY_MISMATCH_COUNT`

A difference between the two regional ratings may also be considered:

`REGION_RATING_DIFF = REGION_RATING_CLIENT_W_CITY - REGION_RATING_CLIENT`

---

### 8. External Data Scores

These columns contain normalized scores obtained from external data sources.

| Column | Meaning |
| --- | --- |
| `EXT_SOURCE_1` | Normalized score from an external data source. |
| `EXT_SOURCE_2` | Normalized score from an external data source. |
| `EXT_SOURCE_3` | Normalized score from an external data source. |

The dataset description identifies these variables as normalized external scores but does not specify the exact underlying source represented by each variable.

They provide additional information about the applicant's **external creditworthiness or risk profile**.

Potential aggregate features include:

`EXT_SOURCE_MEAN`

`EXT_SOURCE_MIN`

`EXT_SOURCE_MAX`

`EXT_SOURCE_STD`

`EXT_SOURCE_MISSING_COUNT`

The individual external scores should also be retained for comparison because different sources may contain different risk signals.

Missingness indicators can be informative and should be evaluated rather than automatically discarded.

---

### 9. Building and Property Characteristics

These columns describe normalized characteristics of the building or property where the client lives.

The variables include measurements of apartment size, living area, land area, common area, building age, building structure, and other property characteristics.

For many numerical building variables, three statistical versions are provided:

* `_AVG` — average value.
* `_MODE` — mode value.
* `_MEDI` — median value.

#### 9.1 Apartment and Area Characteristics

| Column Group | Meaning |
| --- | --- |
| `APARTMENTS_AVG` / `APARTMENTS_MODE` / `APARTMENTS_MEDI` | Normalized apartment-related information. |
| `BASEMENTAREA_AVG` / `BASEMENTAREA_MODE` / `BASEMENTAREA_MEDI` | Normalized basement area information. |
| `COMMONAREA_AVG` / `COMMONAREA_MODE` / `COMMONAREA_MEDI` | Normalized common-area information. |
| `LANDAREA_AVG` / `LANDAREA_MODE` / `LANDAREA_MEDI` | Normalized land-area information. |
| `LIVINGAPARTMENTS_AVG` / `LIVINGAPARTMENTS_MODE` / `LIVINGAPARTMENTS_MEDI` | Normalized living-apartment information. |
| `LIVINGAREA_AVG` / `LIVINGAREA_MODE` / `LIVINGAREA_MEDI` | Normalized living-area information. |
| `NONLIVINGAPARTMENTS_AVG` / `NONLIVINGAPARTMENTS_MODE` / `NONLIVINGAPARTMENTS_MEDI` | Normalized non-living apartment information. |
| `NONLIVINGAREA_AVG` / `NONLIVINGAREA_MODE` / `NONLIVINGAREA_MEDI` | Normalized non-living area information. |

#### 9.2 Building Structure and Age

| Column Group | Meaning |
| --- | --- |
| `YEARS_BEGINEXPLUATATION_AVG` / `YEARS_BEGINEXPLUATATION_MODE` / `YEARS_BEGINEXPLUATATION_MEDI` | Normalized information about when the building began exploitation/use. |
| `YEARS_BUILD_AVG` / `YEARS_BUILD_MODE` / `YEARS_BUILD_MEDI` | Normalized information about the building's construction age. |
| `ELEVATORS_AVG` / `ELEVATORS_MODE` / `ELEVATORS_MEDI` | Normalized information about the number of elevators. |
| `ENTRANCES_AVG` / `ENTRANCES_MODE` / `ENTRANCES_MEDI` | Normalized information about the number of entrances. |
| `FLOORSMAX_AVG` / `FLOORSMAX_MODE` / `FLOORSMAX_MEDI` | Normalized information about the maximum number of floors. |
| `FLOORSMIN_AVG` / `FLOORSMIN_MODE` / `FLOORSMIN_MEDI` | Normalized information about the minimum number of floors. |

#### 9.3 Categorical and General Property Characteristics

| Column | Meaning |
| --- | --- |
| `FONDKAPREMONT_MODE` | Normalized information about the building's fund for major repairs. |
| `HOUSETYPE_MODE` | Most common house/building type. |
| `TOTALAREA_MODE` | Normalized total area information. |
| `WALLSMATERIAL_MODE` | Most common wall material. |
| `EMERGENCYSTATE_MODE` | Emergency-state information about the building. |

These variables provide potential signals related to **housing conditions, property characteristics, and socioeconomic status**.

The building variables are highly related to one another and may contain substantial missingness. Therefore, they should be evaluated using:

* Missing-value analysis.
* Correlation analysis.
* Predictive power such as IV or univariate AUC.
* Redundancy analysis between `_AVG`, `_MODE`, and `_MEDI` versions.
* Stability analysis.

A potential aggregate feature is:

`BUILDING_INFO_MISSING_COUNT`

which counts the number of missing building/property attributes for an applicant.

---

### 10. Social Circle Credit Risk

These columns describe observed payment difficulties among the client's social surroundings.

| Column | Meaning |
| --- | --- |
| `OBS_30_CNT_SOCIAL_CIRCLE` | Number of observations of the client's social surroundings with observable 30 DPD status. |
| `DEF_30_CNT_SOCIAL_CIRCLE` | Number of observations of the client's social surroundings that defaulted at 30 DPD. |
| `OBS_60_CNT_SOCIAL_CIRCLE` | Number of observations of the client's social surroundings with observable 60 DPD status. |
| `DEF_60_CNT_SOCIAL_CIRCLE` | Number of observations of the client's social surroundings that defaulted at 60 DPD. |

These variables provide information about the applicant's **social credit environment**.

Potential derived variables include:

`SOCIAL_30_DEFAULT_RATE = DEF_30_CNT_SOCIAL_CIRCLE / OBS_30_CNT_SOCIAL_CIRCLE`

`SOCIAL_60_DEFAULT_RATE = DEF_60_CNT_SOCIAL_CIRCLE / OBS_60_CNT_SOCIAL_CIRCLE`

The denominator must be handled carefully when the number of observations is zero.

These features should be interpreted as behavioral or contextual risk signals rather than direct evidence that the applicant personally defaulted.

---

### 11. Phone History

| Column | Meaning |
| --- | --- |
| `DAYS_LAST_PHONE_CHANGE` | Number of days before the application when the client last changed their phone. |

The variable can be transformed into an interpretable duration:

`PHONE_CHANGE_DAYS = -DAYS_LAST_PHONE_CHANGE`

Potential categories include:

* Recent phone change.
* Medium-age phone number.
* Long-standing phone number.

The variable may provide information related to contactability and profile stability.

---

### 12. Document Submission

These columns indicate whether specific documents were provided during the application process.

| Column | Meaning |
| --- | --- |
| `FLAG_DOCUMENT_2` | Whether the client provided document 2. |
| `FLAG_DOCUMENT_3` | Whether the client provided document 3. |
| `FLAG_DOCUMENT_4` | Whether the client provided document 4. |
| `FLAG_DOCUMENT_5` | Whether the client provided document 5. |
| `FLAG_DOCUMENT_6` | Whether the client provided document 6. |
| `FLAG_DOCUMENT_7` | Whether the client provided document 7. |
| `FLAG_DOCUMENT_8` | Whether the client provided document 8. |
| `FLAG_DOCUMENT_9` | Whether the client provided document 9. |
| `FLAG_DOCUMENT_10` | Whether the client provided document 10. |
| `FLAG_DOCUMENT_11` | Whether the client provided document 11. |
| `FLAG_DOCUMENT_12` | Whether the client provided document 12. |
| `FLAG_DOCUMENT_13` | Whether the client provided document 13. |
| `FLAG_DOCUMENT_14` | Whether the client provided document 14. |
| `FLAG_DOCUMENT_15` | Whether the client provided document 15. |
| `FLAG_DOCUMENT_16` | Whether the client provided document 16. |
| `FLAG_DOCUMENT_17` | Whether the client provided document 17. |
| `FLAG_DOCUMENT_18` | Whether the client provided document 18. |
| `FLAG_DOCUMENT_19` | Whether the client provided document 19. |
| `FLAG_DOCUMENT_20` | Whether the client provided document 20. |
| `FLAG_DOCUMENT_21` | Whether the client provided document 21. |

The provided data dictionary identifies these variables only by document number and does not specify the exact document represented by each number.

Potential aggregate features include:

`DOCUMENT_COUNT = SUM(FLAG_DOCUMENT_2 ... FLAG_DOCUMENT_21)`

`ANY_DOCUMENT = 1(DOCUMENT_COUNT > 0)`

Individual document flags can also be evaluated for predictive power and stability.

---

### 13. Credit Bureau Enquiries

These columns measure the number of enquiries made to the Credit Bureau during different time periods before the current application.

| Column | Meaning |
| --- | --- |
| `AMT_REQ_CREDIT_BUREAU_HOUR` | Number of Credit Bureau enquiries during the one hour before application. |
| `AMT_REQ_CREDIT_BUREAU_DAY` | Number of Credit Bureau enquiries during the one day before application, excluding the one-hour period. |
| `AMT_REQ_CREDIT_BUREAU_WEEK` | Number of Credit Bureau enquiries during the one week before application, excluding the one-day period. |
| `AMT_REQ_CREDIT_BUREAU_MON` | Number of Credit Bureau enquiries during the one month before application, excluding the one-week period. |
| `AMT_REQ_CREDIT_BUREAU_QRT` | Number of Credit Bureau enquiries during the three months before application, excluding the one-month period. |
| `AMT_REQ_CREDIT_BUREAU_YEAR` | Number of Credit Bureau enquiries during the one year before application, excluding the previous three months. |

These variables provide information about the applicant's **recent credit-seeking activity**.

Higher enquiry activity may indicate increased demand for credit, although it should be interpreted as a risk signal rather than direct evidence of financial distress.

Because the source variables describe mutually separated time windows, cumulative features can be constructed without simply double-counting the same period.

Potential derived features include:

`INQUIRY_1D = HOUR + DAY`

`INQUIRY_1W = HOUR + DAY + WEEK`

`INQUIRY_1M = HOUR + DAY + WEEK + MON`

`INQUIRY_3M = HOUR + DAY + WEEK + MON + QRT`

`INQUIRY_1Y = HOUR + DAY + WEEK + MON + QRT + YEAR`

Potential binary features include:

`HAS_RECENT_INQUIRY`

and an aggregate measure of recent credit-seeking intensity.

---

## Credit Risk Relevance

The `application_train` table provides a broad **current-state risk profile** of each applicant.

Important risk dimensions include:

* **Affordability:** Relationship between income, credit amount, annuity, and goods price.
* **Financial capacity:** Applicant income and socioeconomic characteristics.
* **Employment stability:** Age, employment duration, occupation, and organization type.
* **Household burden:** Number of children and family members.
* **Housing and assets:** Car ownership, car age, housing type, and building characteristics.
* **External creditworthiness:** Normalized external scores.
* **Geographic stability:** Consistency between registered, living, and work addresses.
* **Contactability:** Availability and reachability of communication channels.
* **Social credit environment:** Payment difficulties observed among the client's social surroundings.
* **Credit-seeking behavior:** Frequency of recent Credit Bureau enquiries.
* **Application profile:** Documents and other application characteristics.

The table therefore provides the **static/current application layer** of the credit risk problem.

It should be complemented by historical behavioral information from tables such as `installments_payments`, `previous_application`, `bureau`, `bureau_balance`, `POS_CASH_balance`, and `credit_card_balance`.

---

## Aggregation and Feature Engineering for Credit Scorecard

The `application_train` table is already at the **application level**, with one row corresponding to one `SK_ID_CURR`.

Unlike installment-level or transaction-level tables, it does not require aggregation merely to obtain one row per current application.

However, the raw application variables can be transformed into more informative **application-level risk characteristics**.

### 1. Affordability Features

Potential features include:

* `CREDIT_INCOME`
* `ANNUITY_INCOME`
* `GOODS_INCOME`
* `CREDIT_ANNUITY`

These features measure the size of the current credit obligation relative to the applicant's financial capacity.

### 2. Age and Employment Features

Potential features include:

* `AGE_YEARS`
* `EMPLOYMENT_YEARS`
* Age bands.
* Employment-tenure bands.
* Employment anomaly indicators.

These features describe applicant maturity and employment stability.

### 3. External Score Features

Potential features include:

* Mean external score.
* Minimum external score.
* Maximum external score.
* Standard deviation across external scores.
* Number of missing external scores.

These features summarize both the applicant's overall external score profile and the degree of agreement between external sources.

### 4. Contactability Features

Potential features include:

* Number of available contact channels.
* No-contact-information flag.
* Number of reachable communication channels.

### 5. Geographic Stability Features

Potential features include:

* Total address mismatch count.
* Region mismatch count.
* City mismatch count.
* Difference between regional risk ratings.

### 6. Social Circle Features

Potential features include:

* 30-DPD social default rate.
* 60-DPD social default rate.
* Total social-circle observations.
* Total social-circle defaults.

### 7. Document Features

Potential features include:

* Total number of submitted documents.
* Whether any optional document was submitted.
* Individual document flags where predictive value and stability justify their inclusion.

### 8. Credit-Enquiry Features

Potential features include:

* One-day enquiry count.
* One-week enquiry count.
* One-month enquiry count.
* Three-month enquiry count.
* One-year enquiry count.
* Recent-enquiry indicators.

### 9. Building Features

Potential features include selected property characteristics and missingness indicators.

Because the building variables are numerous and highly correlated, feature selection should be performed rather than automatically retaining every `_AVG`, `_MODE`, and `_MEDI` version.

---

## Feature Engineering Principles

The objective of feature engineering is not to maximize the number of columns.

For a credit scorecard, useful features should ideally have:

* Clear business meaning.
* Predictive power.
* Stable relationship with the target.
* Reasonable missing-value behavior.
* Limited redundancy.
* Interpretability.
* Appropriate monotonicity where required.
* Stability across train/validation or temporal samples.

A practical transformation pipeline is:

`Raw application features`

→ `Data quality checks`

→ `Anomaly and missing-value treatment`

→ `Business-driven feature engineering`

→ `Ratio and aggregate features`

→ `Outlier treatment`

→ `Binning / coarse classing`

→ `WoE transformation`

→ `IV and predictive screening`

→ `Correlation / redundancy analysis`

→ `Feature selection`

→ `Logistic Regression scorecard`

The engineered features from `application_train` can subsequently be combined with aggregated behavioral features from the historical Home Credit tables.

---

## Relationship to Other Tables

The current application is identified by `SK_ID_CURR`.

Historical information can be connected through the current application and previous-credit identifiers.

Conceptually:

`application_train`

→ `SK_ID_CURR`

→ historical previous credits and credit accounts

→ installment/payment behavior

→ aggregated behavioral features

→ final application-level credit risk profile

For example:

`application_train`

provides:

`current income + current credit + current applicant profile`

while:

`installments_payments`

provides:

`historical payment timeliness + payment completeness + repayment consistency`

The combination of current application characteristics and historical repayment behavior provides a substantially richer representation of credit risk than either source alone.

---

## Role in the Credit Scorecard Project

`application_train.csv` is the **central application-level table** of the Home Credit Default Risk dataset.

Its primary role is to provide the applicant's **current financial, demographic, employment, housing, geographic, contact, external-score, social-circle, document, and credit-enquiry characteristics** at the time of the current loan application.

Its main contribution to the scorecard is the construction of features that answer questions such as:

* Can the applicant reasonably afford the requested credit?
* How large is the credit obligation relative to the applicant's income?
* How stable is the applicant's employment and living situation?
* What does external information indicate about the applicant's creditworthiness?
* Does the applicant have a stable and consistent personal profile?
* Is there evidence of credit-seeking activity shortly before the application?
* Are there contextual risk signals from the applicant's social surroundings?
* Does the applicant's housing and socioeconomic profile provide additional risk information?

The `application_train` table should therefore be viewed as the **current-state foundation** of the scorecard, while the remaining Home Credit tables provide historical credit and behavioral information that can be aggregated and joined through `SK_ID_CURR`.

**Source:** Home Credit Default Risk — Kaggle.