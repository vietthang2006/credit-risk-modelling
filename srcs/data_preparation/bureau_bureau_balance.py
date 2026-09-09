import pandas as pd
import numpy as np

class BureauDataPrepare:

    def __init__(self, bureau: pd.DataFrame, bureau_balance: pd.DataFrame):
        self.bureau = bureau
        self.bureau_balance = bureau_balance

    def transform_dtype(self):
        bureau_category_cols = self.bureau.select_dtypes(include=['object', 'str']).columns
        self.bureau[bureau_category_cols] = self.bureau[bureau_category_cols].astype('category')
        bureau_balance_category_cols = self.bureau_balance.select_dtypes(include=['object', 'str']).columns
        self.bureau_balance[bureau_balance_category_cols] = self.bureau_balance[bureau_balance_category_cols].astype('category')

    def bureau_balance_preprocessing(self) -> pd.DataFrame:
        #Encoding bureau status
        status_mapping_dict = {'C': 0, '0': 1, '1': 2, '2': 3, 'X': 4, '3': 5, '4': 6, '5': 7}
        self.bureau_balance['STATUS'] = self.bureau_balance['STATUS'].map(status_mapping_dict).astype('int8')

        # weighted status
        self.bureau_balance['MONTHS_BALANCE'] = np.abs(self.bureau_balance['MONTHS_BALANCE'])
        self.bureau_balance['WEIGHTED_STATUS'] = self.bureau_balance['STATUS'].astype('float') / self.bureau_balance['MONTHS_BALANCE']
        self.bureau_balance = self.bureau_balance.sort_values(by=['SK_ID_BUREAU', 'MONTHS_BALANCE'], ascending=[False, False])

        # EWMA for STATUS and WEIGHTED_STATUS
        self.bureau_balance['EXP_WEIGHTED_STATUS'] = self.bureau_balance.groupby('SK_ID_BUREAU')['WEIGHTED_STATUS'].transform(lambda x: x.ewm(alpha=0.8).mean())
        self.bureau_balance['EXP_STATUS'] = self.bureau_balance.groupby('SK_ID_BUREAU')['STATUS'].transform(lambda x: x.ewm(alpha=0.8).mean())

        # Convert months balance to years balance
        self.bureau_balance['MONTHS_BALANCE'] = self.bureau_balance.MONTHS_BALANCE // 12

        # Statistic aggregation
        aggregation = {
            'MONTHS_BALANCE': ['mean', 'max'],
            'STATUS': ['mean', 'max', 'first'],
            'WEIGHTED_STATUS': ['mean', 'sum','first'],
            'EXP_STATUS': ['last'],
            'EXP_WEIGHTED_STATUS': ['last']
        }

        aggregation_by_year = {
            'STATUS': ['mean', 'max', 'last', 'first'],
            'WEIGHTED_STATUS': ['mean', 'last', 'first', 'max'],
            'EXP_WEIGHTED_STATUS' : ['last'],
            'EXP_STATUS' : ['last'] 
        }

        aggregated_bureau_balance = self.bureau_balance.groupby(['SK_ID_BUREAU']).agg(aggregation)
        aggregated_bureau_balance.columns = ['_'.join(i).upper() for i in aggregated_bureau_balance.columns]

        aggregated_bureau_years = pd.DataFrame()
        for year in range(2):
            year_group = self.bureau_balance[self.bureau_balance['MONTHS_BALANCE'] == year].groupby('SK_ID_BUREAU').agg(aggregation_by_year)
            year_group.columns = ['_'.join(ele).upper() + '_YEAR_' + str(year) for ele in year_group.columns]

            if year == 0:
                aggregated_bureau_years = year_group
            else:
                aggregated_bureau_years = aggregated_bureau_years.merge(year_group, on = 'SK_ID_BUREAU', how = 'outer')

        #aggregating for rest of the years
        aggregated_bureau_rest_years = self.bureau_balance[self.bureau_balance.MONTHS_BALANCE > 1].groupby(['SK_ID_BUREAU']).agg(aggregation_by_year)
        aggregated_bureau_rest_years.columns = ['_'.join(i).upper() + '_YEAR_REST' for i in aggregated_bureau_rest_years.columns]

        #merging with rest of the years
        aggregated_bureau_years = aggregated_bureau_years.merge(aggregated_bureau_rest_years, on = 'SK_ID_BUREAU', how = 'outer')
        aggregated_bureau_balance = aggregated_bureau_balance.merge(aggregated_bureau_years, on = 'SK_ID_BUREAU', how = 'inner')

        return aggregated_bureau_balance

    def bureau_processing(self, aggregated_bureau_balance: pd.DataFrame):
        # Merging bureau with aggregated_bureau_balance\
        bureau_merged = self.bureau.merge(aggregated_bureau_balance, on='SK_ID_BUREAU', how='left')

        # Anomaly value handling 
        col_to_handling_erroneous = ['DAYS_CREDIT_ENDDATE', 'DAYS_ENDDATE_FACT', 'DAYS_CREDIT_UPDATE']
        for col in col_to_handling_erroneous:
            bureau_merged[col][bureau_merged[col] > -50*365] = np.nan

        # Engineering features based on domain knownledge
        bureau_merged['CREDIT_DURATION'] = np.abs(bureau_merged['DAYS_CREDIT'] - bureau_merged['DAYS_CREDIT_ENDDATE'])
        bureau_merged['FLAG_OVERDUE_RECENT'] = [0 if i == 0 else 1 for i in bureau_merged['AMT_CREDIT_MAX_OVERDUE']]
        bureau_merged['MAX_AMT_OVERDUE_DURATION_RATIO'] = bureau_merged['AMT_CREDIT_MAX_OVERDUE'] / (bureau_merged['CREDIT_DURATION'] + 1e-5)
        bureau_merged['CURRENT_AMT_OVERDUE_DURATION_RATIO'] = bureau_merged['AMT_CREDIT_SUM_OVERDUE'] / (bureau_merged['CREDIT_DURATION'] + 1e-5)
        bureau_merged['AMT_OVERDUE_DURATION_LEFT_RATIO'] = bureau_merged['AMT_CREDIT_SUM_OVERDUE'] / (bureau_merged['DAYS_CREDIT_ENDDATE'] + 1e-5)
        bureau_merged['CNT_PROLONGED_MAX_OVERDUE_MUL'] = bureau_merged['CNT_CREDIT_PROLONG'] * bureau_merged['AMT_CREDIT_MAX_OVERDUE']
        bureau_merged['CNT_PROLONGED_DURATION_RATIO'] = bureau_merged['CNT_CREDIT_PROLONG'] / (bureau_merged['CREDIT_DURATION'] + 1e-5)
        bureau_merged['CURRENT_DEBT_TO_CREDIT_RATIO'] = bureau_merged['AMT_CREDIT_SUM_DEBT'] / (bureau_merged['AMT_CREDIT_SUM'] + 1e-5)
        bureau_merged['CURRENT_CREDIT_DEBT_DIFF'] = bureau_merged['AMT_CREDIT_SUM'] - bureau_merged['AMT_CREDIT_SUM_DEBT']
        bureau_merged['AMT_ANNUITY_CREDIT_RATIO'] = bureau_merged['AMT_ANNUITY'] / (bureau_merged['AMT_CREDIT_SUM'] + 1e-5)
        bureau_merged['CREDIT_ENDDATE_UPDATE_DIFF'] = np.abs(bureau_merged['DAYS_CREDIT_UPDATE'] - bureau_merged['DAYS_CREDIT_ENDDATE'])

        aggregations_CREDIT_ACTIVE = {
            'DAYS_CREDIT' : ['mean','min','max','last'],
            'CREDIT_DAY_OVERDUE' : ['mean','max'],
            'DAYS_CREDIT_ENDDATE' : ['mean','max'],
            'DAYS_ENDDATE_FACT' : ['mean','min'],
            'AMT_CREDIT_MAX_OVERDUE': ['max','sum', 'mean'],
            'CNT_CREDIT_PROLONG': ['max','sum', 'mean'],
            'AMT_CREDIT_SUM' : ['sum','max'],
            'AMT_CREDIT_SUM_DEBT': ['sum'],
            'AMT_CREDIT_SUM_LIMIT': ['max','sum'],
            'AMT_CREDIT_SUM_OVERDUE': ['max','sum'],
            'DAYS_CREDIT_UPDATE' : ['mean','min'],
            'AMT_ANNUITY' : ['mean','sum','max'],
            'CREDIT_DURATION' : ['max','mean'],
            'FLAG_OVERDUE_RECENT': ['sum'],
            'MAX_AMT_OVERDUE_DURATION_RATIO' : ['max','sum'],
            'CURRENT_AMT_OVERDUE_DURATION_RATIO' : ['max','sum'],
            'AMT_OVERDUE_DURATION_LEFT_RATIO' : ['max', 'mean'],
            'CNT_PROLONGED_MAX_OVERDUE_MUL' : ['mean','max'],
            'CNT_PROLONGED_DURATION_RATIO' : ['mean', 'max'],
            'CURRENT_DEBT_TO_CREDIT_RATIO' : ['mean', 'min'],
            'CURRENT_CREDIT_DEBT_DIFF' : ['mean','min'],
            'AMT_ANNUITY_CREDIT_RATIO' : ['mean','max','min'],
            'CREDIT_ENDDATE_UPDATE_DIFF' : ['max','min'],
            'STATUS_MEAN' : ['mean', 'max'],
            'WEIGHTED_STATUS_MEAN' : ['mean', 'max']
        }

        categories_to_aggregate_on = ['Closed','Active']
        bureau_merged_aggregated_credit = pd.DataFrame()
        for i, status in enumerate(categories_to_aggregate_on):
            group = bureau_merged[bureau_merged['CREDIT_ACTIVE'] == status].groupby('SK_ID_CURR').agg(aggregations_CREDIT_ACTIVE)
            group.columns = ['_'.join(ele).upper() + '_CREDITACTIVE_' + status.upper() for ele in group.columns]
            if i==0:
                bureau_merged_aggregated_credit = group
            else:
                bureau_merged_aggregated_credit = bureau_merged_aggregated_credit.merge(group, on = 'SK_ID_CURR', how = 'outer')
        
        bureau_merged_aggregated_credit_rest = bureau_merged[(bureau_merged['CREDIT_ACTIVE'] != 'Active') & (bureau_merged['CREDIT_ACTIVE'] != 'Closed')].groupby('SK_ID_CURR').agg(aggregations_CREDIT_ACTIVE)
        bureau_merged_aggregated_credit_rest.columns = ['_'.join(ele).upper() + 'CREDIT_ACTIVE_REST' for ele in bureau_merged_aggregated_credit_rest.columns]
        bureau_merged_aggregated_credit = bureau_merged_aggregated_credit.merge(bureau_merged_aggregated_credit_rest, on = 'SK_ID_CURR', how = 'outer')

        #Encoding the categorical columns in one-hot form
        currency_ohe = pd.get_dummies(bureau_merged['CREDIT_CURRENCY'], prefix = 'CURRENCY')
        credit_active_ohe = pd.get_dummies(bureau_merged['CREDIT_ACTIVE'], prefix = 'CREDIT_ACTIVE')
        credit_type_ohe = pd.get_dummies(bureau_merged['CREDIT_TYPE'], prefix = 'CREDIT_TYPE')
        bureau_merged = pd.concat([bureau_merged.drop(['CREDIT_CURRENCY','CREDIT_ACTIVE','CREDIT_TYPE'], axis = 1), currency_ohe, credit_active_ohe, credit_type_ohe], axis = 1)

        #aggregating the bureau_merged over all the columns
        bureau_merged_aggregated = bureau_merged.drop('SK_ID_BUREAU', axis = 1).groupby('SK_ID_CURR').agg('mean')
        bureau_merged_aggregated.columns = [ele + '_MEAN_OVERALL' for ele in bureau_merged_aggregated.columns]
        bureau_merged_aggregated = bureau_merged_aggregated.merge(bureau_merged_aggregated_credit, on = 'SK_ID_CURR', how = 'outer')

        return bureau_merged_aggregated

    def main(self):
        self.transform_dtype()
        aggregated_bureau_balance = self.bureau_balance_preprocessing()
        bureau_merged_aggregated = self.bureau_processing(aggregated_bureau_balance)
        
        return bureau_merged_aggregated