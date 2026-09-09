import pandas as pd
import numpy as np

class CreditCardBalancePrepare:
    def __init__(self, df: pd.DataFrame):
        self.df = df 

    def credit_card_balance_preprocessing(self):
        self.df['AMT_PAYMENT_CURRENT'][self.df['AMT_PAYMENT_CURRENT'] > 4000000] = np.nan
        self.df['MISSING_TOTAL_VALUES_CC'] = self.df.isna().sum(axis=1)
        self.df['MONTHS_BALANCE'] = np.abs(self.df['MONTHS_BALANCE'])
        self.df = self.df.sort_values(by=['SK_ID_PREV', 'MONTHS_BALANCE'], ascending=[True, False])

    def credit_card_balance_engineering(self):
        amt_drawing_cols = ['AMT_DRAWINGS_ATM_CURRENT', 'AMT_DRAWINGS_CURRENT', 'AMT_DRAWINGS_OTHER_CURRENT', 'AMT_DRAWINGS_POS_CURRENT']  
        self.df['AMT_DRAWING_SUM'] = self.df[amt_drawing_cols].sum(axis=1)
        self.df['BALANCE_LIMIT_RATIO'] = self.df['AMT_BALANCE'] / (self.df['AMT_CREDIT_LIMIT_ACTUAL'] + 1e-5)
        cnt_drawings_cols = ['CNT_DRAWINGS_ATM_CURRENT', 'CNT_DRAWINGS_CURRENT', 'CNT_DRAWINGS_OTHER_CURRENT', 'CNT_DRAWINGS_POS_CURRENT', 'CNT_INSTALMENT_MATURE_CUM']
        self.df['CNT_DRAWING_SUM'] = self.df[cnt_drawings_cols].sum(axis=1)
        self.df['MIN_PAYMENT_RATIO'] = self.df['AMT_PAYMENT_CURRENT'] / (self.df['AMT_INST_MIN_REGULARITY'] + 1e-5)
        self.df['PAYMENT_MIN_DIFF'] = self.df['AMT_PAYMENT_CURRENT'] - self.df['AMT_INST_MIN_REGULARITY']
        self.df['MIN_PAYMENT_TOTAL_RATIO'] = self.df['AMT_PAYMENT_TOTAL_CURRENT'] / (self.df['AMT_INST_MIN_REGULARITY'] + 1e-5)
        self.df['PAYMENT_MIN_TOTAL_RATIO'] = self.df['AMT_PAYMENT_TOTAL_CURRENT'] - self.df['AMT_INST_MIN_REGULARITY']
        self.df['AMT_INTEREST_RECEIVABLE'] = self.df['AMT_TOTAL_RECEIVABLE'] - self.df['AMT_RECEIVABLE_PRINCIPAL']
        self.df['SK_DPD_RATIO'] = self.df['SK_DPD'] / (self.df['SK_DPD_DEF'] + 1e-5)

        # Rolling Exponential Weighted Moving Average Columns by times
        rolling_cols = [
            'AMT_BALANCE',
            'AMT_CREDIT_LIMIT_ACTUAL', 
            'AMT_RECEIVABLE_PRINCIPAL', 
            'AMT_RECIVABLE',
            'AMT_TOTAL_RECEIVABLE',
            'AMT_DRAWING_SUM', 
            'BALANCE_LIMIT_RATIO',
            'CNT_DRAWING_SUM', 
            'MIN_PAYMENT_RATIO', 
            'PAYMENT_MIN_DIFF',
            'MIN_PAYMENT_TOTAL_RATIO',
            'AMT_INTEREST_RECEIVABLE',
            'SK_DPD_RATIO'
        ]

        ewma_columns = ['EXP_' + i for i in rolling_cols]
        self.df[ewma_columns] = self.df.groupby(['SK_ID_CURR', 'SK_ID_PREV'])[rolling_cols].transform(lambda x: x.ewm(alpha=0.7).mean())

    def aggregation(self):

        # Overall Aggregations
        overall_aggregations = {
            'SK_ID_CURR' : ['first'],
            'MONTHS_BALANCE': ['max'],
            'AMT_BALANCE' : ['sum','mean','max'],
            'AMT_CREDIT_LIMIT_ACTUAL' : ['sum','mean','max'],
            'AMT_DRAWINGS_ATM_CURRENT' : ['sum','max'],
            'AMT_DRAWINGS_CURRENT' : ['sum','max'],
            'AMT_DRAWINGS_OTHER_CURRENT' : ['sum','max'],
            'AMT_DRAWINGS_POS_CURRENT' : ['sum','max'],
            'AMT_INST_MIN_REGULARITY' : ['mean','min','max'],
            'AMT_PAYMENT_CURRENT' : ['mean','min','max'],
            'AMT_PAYMENT_TOTAL_CURRENT' : ['mean','min','max'],
            'AMT_RECEIVABLE_PRINCIPAL' : ['sum','mean','max'],
            'AMT_RECIVABLE' : ['sum','mean','max'],
            'AMT_TOTAL_RECEIVABLE' : ['sum','mean','max'],
            'CNT_DRAWINGS_ATM_CURRENT' : ['sum','max'],
            'CNT_DRAWINGS_CURRENT' : ['sum','max'],
            'CNT_DRAWINGS_OTHER_CURRENT' : ['sum','max'],
            'CNT_DRAWINGS_POS_CURRENT' : ['sum','max'],
            'CNT_INSTALMENT_MATURE_CUM' : ['sum','max','min'],
            'SK_DPD' : ['sum','max'],
            'SK_DPD_DEF' : ['sum','max'],

            'AMT_DRAWING_SUM' : ['sum','max'],
            'BALANCE_LIMIT_RATIO' : ['mean','max','min'],
            'CNT_DRAWING_SUM' : ['sum','max'],
            'MIN_PAYMENT_RATIO': ['min','mean'],
            'PAYMENT_MIN_DIFF' : ['min','mean'],
            'MIN_PAYMENT_TOTAL_RATIO' : ['min','mean'], 
            'AMT_INTEREST_RECEIVABLE' : ['min','mean'],
            'SK_DPD_RATIO' : ['max','mean'],

            'EXP_AMT_BALANCE' : ['last'],
            'EXP_AMT_CREDIT_LIMIT_ACTUAL' : ['last'],
            'EXP_AMT_RECEIVABLE_PRINCIPAL' : ['last'],
            'EXP_AMT_RECIVABLE' : ['last'],
            'EXP_AMT_TOTAL_RECEIVABLE' : ['last'],
            'EXP_AMT_DRAWING_SUM' : ['last'],
            'EXP_BALANCE_LIMIT_RATIO' : ['last'],
            'EXP_CNT_DRAWING_SUM' : ['last'],
            'EXP_MIN_PAYMENT_RATIO' : ['last'],
            'EXP_PAYMENT_MIN_DIFF' : ['last'],
            'EXP_MIN_PAYMENT_TOTAL_RATIO' : ['last'],
            'EXP_AMT_INTEREST_RECEIVABLE' : ['last'],
            'EXP_SK_DPD_RATIO' : ['last'],
            'MISSING_TOTAL_VALUES_CC' : ['sum']
        }
        credit_card_balance_overall = self.df.groupby('SK_ID_PREV').agg(overall_aggregations)
        credit_card_balance_overall.columns = ['_'.join(i).upper() + '_OVERALL' for i in credit_card_balance_overall.columns]
        credit_card_balance_overall.rename(columns={'SK_ID_CURR_FIRST_OVERALL': 'SK_ID_CURR'}, inplace=True)

        # Categories Aggregations
        aggregations_for_categories = {
            'SK_DPD' : ['sum','max'],
            'SK_DPD_DEF' : ['sum','max'],
            'BALANCE_LIMIT_RATIO' : ['mean','max','min'],
            'CNT_DRAWING_SUM' : ['sum','max'],
            'MIN_PAYMENT_RATIO': ['min','mean'],
            'PAYMENT_MIN_DIFF' : ['min','mean'],
            'MIN_PAYMENT_TOTAL_RATIO' : ['min','mean'], 
            'AMT_INTEREST_RECEIVABLE' : ['min','mean'],
            'SK_DPD_RATIO' : ['max','mean'],
            'EXP_AMT_DRAWING_SUM' : ['last'],
            'EXP_BALANCE_LIMIT_RATIO' : ['last'],
            'EXP_CNT_DRAWING_SUM' : ['last'],
            'EXP_MIN_PAYMENT_RATIO' : ['last'],
            'EXP_PAYMENT_MIN_DIFF' : ['last'],
            'EXP_MIN_PAYMENT_TOTAL_RATIO' : ['last'],
            'EXP_AMT_INTEREST_RECEIVABLE' : ['last'],
            'EXP_SK_DPD_RATIO' : ['last']
        }
        contract_status = ['Active', 'Completed']
        credit_card_balance_categories = None
        for status in contract_status:
            group = self.df[self.df['NAME_CONTRACT_STATUS'] == status].groupby('SK_ID_PREV').agg(aggregations_for_categories)
            group.columns = ['_'.join(col).upper() + '_' + status.upper() for col in group.columns]
            if credit_card_balance_categories is None:
                credit_card_balance_categories = group
            else:
                credit_card_balance_categories = credit_card_balance_categories.merge(group, on='SK_ID_PREV', how='outer')

        # safe filter for remaining contract statuses
        remaining_mask = (self.df['NAME_CONTRACT_STATUS'] != 'Active') & (self.df['NAME_CONTRACT_STATUS'] != 'Completed')
        credit_card_balance_categories_remaining = self.df[remaining_mask].groupby('SK_ID_PREV').agg(aggregations_for_categories)
        credit_card_balance_categories_remaining.columns = ['_'.join(i).upper() + '_REST' for i in credit_card_balance_categories_remaining.columns]

        # If no categories were created in the loop above, use the remaining as the base
        if credit_card_balance_categories is None:
            credit_card_balance_categories = credit_card_balance_categories_remaining
        else:
            credit_card_balance_categories = credit_card_balance_categories.merge(credit_card_balance_categories_remaining, on='SK_ID_PREV', how='outer')

        # Aggregations Years

        aggregations_for_year = {
            'SK_DPD' : ['sum','max'],
            'SK_DPD_DEF' : ['sum','max'],
            'BALANCE_LIMIT_RATIO' : ['mean','max','min'],
            'CNT_DRAWING_SUM' : ['sum','max'],
            'MIN_PAYMENT_RATIO': ['min','mean'],
            'PAYMENT_MIN_DIFF' : ['min','mean'],
            'MIN_PAYMENT_TOTAL_RATIO' : ['min','mean'], 
            'AMT_INTEREST_RECEIVABLE' : ['min','mean'],
            'SK_DPD_RATIO' : ['max','mean'],
            'EXP_AMT_DRAWING_SUM' : ['last'],
            'EXP_BALANCE_LIMIT_RATIO' : ['last'],
            'EXP_CNT_DRAWING_SUM' : ['last'],
            'EXP_MIN_PAYMENT_RATIO' : ['last'],
            'EXP_PAYMENT_MIN_DIFF' : ['last'],
            'EXP_MIN_PAYMENT_TOTAL_RATIO' : ['last'],
            'EXP_AMT_INTEREST_RECEIVABLE' : ['last'],
            'EXP_SK_DPD_RATIO' : ['last']
        }
        self.df['YEARS_BALANCE'] = self.df['MONTHS_BALANCE'] // 12
        credit_card_balance_different_years = None
        for year in range(2):
            group = self.df[self.df['YEARS_BALANCE'] == year].groupby('SK_ID_PREV').agg(aggregations_for_year)
            group.columns = ['_'.join(col).upper() + f'_YEAR_{year}' for col in group.columns]
            if credit_card_balance_different_years is None:
                credit_card_balance_different_years = group
            else:
                credit_card_balance_different_years = credit_card_balance_different_years.merge(group, on='SK_ID_PREV', how='outer')

        # The rest years
        credit_card_balance_different_years_remaining = self.df[self.df['YEARS_BALANCE'] >= 2].groupby('SK_ID_PREV').agg(aggregations_for_year)
        credit_card_balance_different_years_remaining.columns = ['_'.join(i).upper() + '_REST' for i in credit_card_balance_different_years_remaining.columns]

        if credit_card_balance_different_years is None:
            credit_card_balance_different_years = credit_card_balance_different_years_remaining
        else:
            credit_card_balance_different_years = credit_card_balance_different_years.merge(credit_card_balance_different_years_remaining, on='SK_ID_PREV', how='outer')        
        self.df = self.df.drop('YEARS_BALANCE', axis=1)

        # Merging all aggregated table
        cc_aggregated = credit_card_balance_overall.merge(credit_card_balance_categories, on='SK_ID_PREV', how='outer')
        cc_aggregated = cc_aggregated.merge(credit_card_balance_different_years, on='SK_ID_PREV', how='outer')

        # One-hot encoding for NAME_CONTRACT_STATUS
        contract_status_ohe = pd.get_dummies(self.df.NAME_CONTRACT_STATUS, prefix='CONTRACT')
        contract_names = contract_status_ohe.columns.tolist()

        self.df = pd.concat([self.df, contract_status_ohe], axis=1)
        aggregated_cc_contract = self.df[['SK_ID_PREV'] + contract_names].groupby('SK_ID_PREV').mean()
        cc_aggregated = cc_aggregated.merge(aggregated_cc_contract, on='SK_ID_PREV', how='outer')
        cc_aggregated = cc_aggregated.groupby('SK_ID_CURR', as_index=False).mean()

        return cc_aggregated

    def main(self):
        self.credit_card_balance_preprocessing()
        self.credit_card_balance_engineering()
        cc_aggregated = self.aggregation()
        return cc_aggregated