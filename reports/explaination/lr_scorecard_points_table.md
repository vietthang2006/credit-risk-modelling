# Credit Scorecard Scaling Table (Logistic Regression)

**Parameters**: Base Score = 600 points @ Odds 50:1 (Good:Bad) | PDO = 20 points

| Feature | Coefficient (beta) | Odds Ratio | Std_Dev | Points_Delta_per_Std | Risk_Direction |
| --- | --- | --- | --- | --- | --- |
| EXPECTED_INTEREST | 0.8445 | 2.3268 | 718416.4935 | -17505788.7 | High Risk (Decreases Score) |
| EXPECTED_CNT_PAYMENT | -0.8264 | 0.4376 | 18.5014 | 441.2 | Low Risk (Increases Score) |
| DAYS_BIRTH | 0.7943 | 2.213 | 11.9483 | -273.9 | High Risk (Decreases Score) |
| EXT_SOURCE_1 | -0.7774 | 0.4596 | 0.1808 | 4.1 | Low Risk (Increases Score) |
| EXPECTED_INTEREST_SHARE | 0.522 | 1.6854 | 0.5513 | -8.3 | High Risk (Decreases Score) |
| AMT_GOODS_PRICE | -0.5 | 0.6065 | 369389.8788 | 5328959.0 | Low Risk (Increases Score) |
| CREDIT_ANNUITY_RATIO | 0.4239 | 1.5279 | 7.8138 | -95.6 | High Risk (Decreases Score) |
| AMT_CREDIT | -0.4186 | 0.658 | 402503.1441 | 4861084.6 | Low Risk (Increases Score) |
| AMT_CREDIT_SUM_SUM_CREDITACTIVE_ACTIVE | 0.4079 | 1.5036 | 2270374.9557 | -26718057.7 | High Risk (Decreases Score) |
| EXT_SOURCE_MEAN | -0.396 | 0.673 | 0.1299 | 1.5 | Low Risk (Increases Score) |
| AGE_EMPLOYED_DIFF | 0.3691 | 1.4465 | 394.1805 | -4198.3 | High Risk (Decreases Score) |
| DAYS_EMPLOYED | -0.3517 | 0.7035 | 386.7087 | 3924.4 | Low Risk (Increases Score) |
| WEIGHTED_EXT_SOURCE | -0.3061 | 0.7363 | 1.0526 | 9.3 | Low Risk (Increases Score) |
| AMT_ANNUITY | 0.2495 | 1.2834 | 14547.9521 | -104737.3 | High Risk (Decreases Score) |
| CURRENT_CREDIT_DEBT_DIFF_MEAN_CREDITACTIVE_ACTIVE | -0.2471 | 0.7811 | 405833.6051 | 2893218.5 | Low Risk (Increases Score) |
| AMT_CREDIT_SUM_MAX_CREDITACTIVE_ACTIVE | -0.2383 | 0.788 | 1638264.8594 | 11263787.4 | Low Risk (Increases Score) |
| AGE_EMPLOYED_DIFF_MEAN_AGG_CODE_GENDER_NAME_FAMILY_STATUS_NAME_INCOME_TYPE | -0.2259 | 0.7978 | 394.0288 | 2568.4 | Low Risk (Increases Score) |
| EXT_SOURCE_MUL_SQRT | -0.2237 | 0.7995 | 0.1476 | 1.0 | Low Risk (Increases Score) |
| AMT_PAYMENT_SUM_LAST_1_YEAR | -0.2128 | 0.8083 | 257410.941 | 1580285.0 | Low Risk (Increases Score) |
| EXPECTED_INTEREST_RATE | -0.2055 | 0.8142 | 0.6049 | 3.6 | Low Risk (Increases Score) |
| AMT_INSTALMENT_MAX_LAST_1_YEAR | 0.2041 | 1.2264 | 143247.0774 | -843566.4 | High Risk (Decreases Score) |
| CURRENCY_currency 1_MEAN_OVERALL | 0.2003 | 1.2218 | 0.3502 | -2.0 | High Risk (Decreases Score) |
| ORGANIZATION_TYPE | -0.1907 | 0.8264 | 0.2832 | 1.6 | Low Risk (Increases Score) |
| AMT_PAYMENT_RATIO_MIN_LAST_1_YEAR | -0.1682 | 0.8452 | 0.4653 | 2.3 | Low Risk (Increases Score) |
| AGE_EMPLOYED_DIFF_MEAN_AGG_NAME_EDUCATION_TYPE_NAME_INCOME_TYPE_OCCUPATION_TYPE | -0.1552 | 0.8563 | 394.0404 | 1764.1 | Low Risk (Increases Score) |