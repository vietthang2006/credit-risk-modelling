import pandas as pd
import numpy as np

class POSCashBalancePrepare:

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def pos_cash_preprocessing(self):
        self.df['MONTHS_BALANCE'] = np.abs(self.df['MONTHS_BALANCE'])
        self.df = self.df.sort_values(by=['SK_ID_PREV', 'MONTHS_BALANCE'], ascending=False)

    def pos_cash_feature_engineering(self):
        self.df['SK_DPD_RATIO'] = self.df['SK_DPD'] / (self.df['SK_DPD_DEF'] + 1e-5)
        self.df['TOTAL_TERM'] = self.df['CNT_INSTALMENT'] + self.df['CNT_INSTALMENT_FUTURE']
        #EWMA feature
        ewma_cols = ['CNT_INSTALMENT', 'CNT_INSTALMENT_FUTURE']
        exp_cols = ['EXP_' + col for col in ewma_cols]
        self.df[exp_cols] = self.df.groupby('SK_ID_PREV')[ewma_cols].transform(lambda x: x.ewm(alpha=0.65).mean())
        self.df['EXP_POS_TOTAL_TERM'] = self.df['EXP_CNT_INSTALMENT'] + self.df['EXP_CNT_INSTALMENT_FUTURE']

    def aggregation_sk_id_prev(self):

        # Overall Aggregation
        overall_aggregations = {
            'SK_ID_CURR': ['first'],
            'MONTHS_BALANCE': ['max'],
            'CNT_INSTALMENT': ['max', 'min', 'mean'],
            'CNT_INSTALMENT_FUTURE': ['max', 'min', 'mean'],
            'SK_DPD': ['max', 'sum'],
            'SK_DPD_DEF': ['max', 'sum'],
            'EXP_CNT_INSTALMENT': ['last'],
            'EXP_CNT_INSTALMENT_FUTURE': ['last'],
            'SK_DPD_RATIO': ['mean', 'max'],
            'TOTAL_TERM': ['mean', 'max'],
            'EXP_POS_TOTAL_TERM': ['last']
        }

        pos_cash_overall_agg = self.df.groupby('SK_ID_PREV').agg(overall_aggregations)
        pos_cash_overall_agg.columns = ['_'.join(i).upper() for i in pos_cash_overall_agg.columns]
        pos_cash_overall_agg.rename(columns={'SK_ID_CURR_FIRST': 'SK_ID_CURR'}, inplace=True)

        # Yearwise Aggregation
        year_aggregations = {
            'CNT_INSTALMENT': ['mean', 'max', 'min'],
            'CNT_INSTALMENT_FUTURE': ['max', 'min', 'mean'],
            'SK_DPD': ['max', 'sum'],
            'SK_DPD_DEF': ['max', 'sum'],
            'EXP_CNT_INSTALMENT' : ['last'],
            'EXP_CNT_INSTALMENT_FUTURE' : ['last'],    
            'SK_DPD_RATIO': ['mean', 'max'],
            'TOTAL_TERM': ['mean', 'max'],
            'EXP_POS_TOTAL_TERM': ['last']
        }
        #last 2 years
        pos_cash_year_agg = None

        for year in range(2):
            group = self.df[self.df['MONTHS_BALANCE'] // 12 == year].groupby('SK_ID_PREV').agg(year_aggregations)
            group.columns = ['_'.join(i).upper() + f'_YEAR_{year}' for i in group.columns]
            if pos_cash_year_agg is None:
                pos_cash_year_agg = group
            else:
                pos_cash_year_agg = pos_cash_year_agg.merge(group, on='SK_ID_PREV', how='outer')

        pos_cash_rest_year_agg = self.df[self.df['MONTHS_BALANCE'] // 12 >= 2].groupby('SK_ID_PREV').agg(year_aggregations)
        pos_cash_rest_year_agg.columns = ['_'.join(i).upper() + '_YEAR_REST' for i in pos_cash_rest_year_agg.columns]
        if pos_cash_year_agg is None:
            pos_cash_year_agg = pos_cash_rest_year_agg
        else:
            pos_cash_year_agg = pos_cash_year_agg.merge(pos_cash_rest_year_agg, on='SK_ID_PREV', how='outer')

        # Categories Aggregation
        categories_aggregation = {
            'CNT_INSTALMENT': ['mean', 'max', 'min'],
            'CNT_INSTALMENT_FUTURE': ['max', 'min', 'mean'],
            'SK_DPD': ['max', 'sum'],
            'SK_DPD_DEF': ['max', 'sum'],
            'EXP_CNT_INSTALMENT' : ['last'],
            'EXP_CNT_INSTALMENT_FUTURE' : ['last'],    
            'SK_DPD_RATIO': ['mean', 'max'],
            'TOTAL_TERM': ['mean', 'max'],
            'EXP_POS_TOTAL_TERM': ['last']
        }

        contract_type_categories = ['Active', 'Completed']
        pos_cash_category_agg = None

        for type in contract_type_categories:
            group = self.df[self.df['NAME_CONTRACT_STATUS'] == type].groupby('SK_ID_PREV').agg(categories_aggregation)
            group.columns = ['_'.join(i).upper() + '_' + type.upper() for i in group.columns]
            if pos_cash_category_agg is None:
                pos_cash_category_agg = group
            else:
                pos_cash_category_agg = pos_cash_category_agg.merge(group, on='SK_ID_PREV', how='outer')

        mask = ~(self.df['NAME_CONTRACT_STATUS'].isin(contract_type_categories))
        pos_cash_other_category_agg = self.df[mask].groupby('SK_ID_PREV').agg(categories_aggregation)
        pos_cash_other_category_agg.columns = ['_'.join(i).upper() + '_REST' for i in pos_cash_other_category_agg.columns]
        if pos_cash_category_agg is None:
            pos_cash_category_agg = pos_cash_other_category_agg
        else:
            pos_cash_category_agg = pos_cash_category_agg.merge(pos_cash_other_category_agg, on='SK_ID_PREV', how='outer')

        pos_cash_aggregated = pos_cash_overall_agg.merge(pos_cash_year_agg, on='SK_ID_PREV', how='outer')
        pos_cash_aggregated = pos_cash_aggregated.merge(pos_cash_category_agg, on='SK_ID_PREV', how='outer')

        # One hot encoding for NAME_CONTRACT_STATUS
        name_contract_status_ohe = pd.get_dummies(self.df['NAME_CONTRACT_STATUS'], prefix='CONTRACT')
        contract_names = name_contract_status_ohe.columns.tolist()

        self.df = pd.concat([self.df, name_contract_status_ohe], axis=1)
        aggregated_cc_contract = self.df[['SK_ID_PREV'] + contract_names].groupby('SK_ID_PREV').mean()   
        pos_cash_aggregated = pos_cash_aggregated.merge(aggregated_cc_contract, on='SK_ID_PREV', how='outer')

        return pos_cash_aggregated

    def aggregations_sk_id_curr(self, pos_cash_aggregated: pd.DataFrame):
    
        #aggregating over SK_ID_CURR
        columns_to_aggregate = pos_cash_aggregated.columns[1:]
        #defining the aggregations to perform
        aggregations_final = {}
        for col in columns_to_aggregate:
            if 'MEAN' in col:
                aggregates = ['mean','sum','max']
            else:
                aggregates = ['mean']
            aggregations_final[col] = aggregates
        pos_cash_aggregated_final = pos_cash_aggregated.groupby('SK_ID_CURR').agg(aggregations_final)
        pos_cash_aggregated_final.columns = ['_'.join(ele).upper() for ele in pos_cash_aggregated_final.columns]
        
        return pos_cash_aggregated_final

    def main(self):
        self.pos_cash_preprocessing()
        self.pos_cash_feature_engineering()
        df = self.aggregation_sk_id_prev()
        final = self.aggregations_sk_id_curr(df)
        return final