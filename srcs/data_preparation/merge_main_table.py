import pandas as pd
import numpy as np

def merge_main_table(
    application: pd.DataFrame,
    agg_bureau: pd.DataFrame,
    agg_prev_application: pd.DataFrame,
    agg_cc_balance: pd.DataFrame,
    agg_pos_cash: pd.DataFrame,
    agg_installment_payment: pd.DataFrame
) -> pd.DataFrame:

    # Merge agg_bureau
    merge_application = application.merge(agg_bureau, on='SK_ID_CURR', how='left')

    # Merge agg_prev_application
    merge_application = merge_application.merge(agg_prev_application, on='SK_ID_CURR', how='left')

    # Merge agg_cc_balance
    merge_application = merge_application.merge(agg_cc_balance, on='SK_ID_CURR', how='left')

    # Merge agg_pos_cash
    merge_application = merge_application.merge(agg_pos_cash, on='SK_ID_CURR', how='left')

    # Merge agg_installment_payment
    merge_application = merge_application.merge(agg_installment_payment, on='SK_ID_CURR', how='left')

    # FEATURE ENGINEERING FOR MERGE TABLE
    # agg_prev_application
    prev_annuity_cols = [col for col in agg_prev_application.columns if 'AMT_ANNUITY' in col]
    for col in prev_annuity_cols:
        merge_application['PREV_' + col + '_INCOME_TOTAL'] = merge_application[col] / (merge_application['AMT_INCOME_TOTAL'] + 1e-5)

    prev_goods_cols = [col for col in agg_prev_application.columns if 'AMT_GOODS' in col]
    for col in prev_goods_cols:
        merge_application['PREV_' + col + '_INCOME_TOTAL'] = merge_application[col] / (merge_application['AMT_INCOME_TOTAL'] + 1e-5)

    # agg_cc_balance
    cc_amt_receivable = [col for col in agg_cc_balance.columns if 'AMT_RECEIVABLE' in col]
    for col in cc_amt_receivable:
        merge_application['CC_BALANCE_' + col + '_AMT_INCOME_TOTAL'] = merge_application[col] / (merge_application['AMT_INCOME_TOTAL'] + 1e-5)

    cc_amt_principal = [col for col in agg_cc_balance.columns if 'AMT_RECEIVABLE_PRINCIPAL' in col]
    for col in cc_amt_principal:
        merge_application['CC_BALANCE_' + col + '_AMT_INCOME_TOTAL'] = merge_application[col] / (merge_application['AMT_INCOME_TOTAL'] + 1e-5)

    # agg_installment_payment
    instalment_payment_col = [col for col in agg_installment_payment.columns if 'AMT_PAYMENT' in col]
    for col in instalment_payment_col:
        merge_application['INST_PAYT_' + col + '_AMT_INCOME_TOTAL'] = merge_application[col] / (merge_application['AMT_INCOME_TOTAL'] + 1e-5)

    # agg_bureau
    bureau_days_credit_cols = [col for col in agg_bureau.columns if 'DAYS_CREDIT' in col and 'ENDDATE' not in col and 'UPDATE' not in col]
    for col in bureau_days_credit_cols:
        merge_application['BUREAU_' + col + '_EMPLOYED_DIFF'] = merge_application[col] - merge_application['DAYS_EMPLOYED']
        merge_application['BUREAU_' + col + '_REGISTRATION_DIFF'] = merge_application[col] - merge_application['DAYS_REGISTRATION']
    bureau_overdue_cols = [col for col in agg_bureau.columns if 'AMT_CREDIT' in col and 'OVERDUE' in col]
    for col in bureau_overdue_cols:
        merge_application['BUREAU_' + col + '_INCOME_RATIO'] = merge_application[col] /(merge_application['AMT_INCOME_TOTAL'] + 1e-5)
    bureau_amt_annuity_cols = [col for col in agg_bureau.columns if 'AMT_ANNUITY' in col and 'CREDIT' not in col]
    for col in bureau_amt_annuity_cols:
        merge_application['BUREAU_' + col + '_INCOME_RATIO'] = merge_application[col] / (merge_application['AMT_INCOME_TOTAL'] + 1e-5)

    return merge_application