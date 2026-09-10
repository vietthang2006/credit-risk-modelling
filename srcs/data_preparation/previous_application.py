import numpy as np
import pandas as pd

class PreviousApplicationPrepare:

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def data_cleaning(self):
        # Handle errorneous value
        for col in ['DAYS_FIRST_DRAWING', 'DAYS_FIRST_DUE', 'DAYS_LAST_DUE_1ST_VERSION', 'DAYS_LAST_DUE', 'DAYS_TERMINATION']:
            self.df[col][self.df[col] == 365243.0] = np.nan

        # SELLERPLACE_AREA
        self.df['SELLERPLACE_AREA'][self.df['SELLERPLACE_AREA'] == 4000000] = np.nan
        # Impute missing value in categorical columns
        categorical_columns = self.df.dtypes[self.df.dtypes == 'object'].index.tolist()
        self.df[categorical_columns] = self.df[categorical_columns].fillna('XNA')

    def feature_engineering(self):
        """
        Function is used to encode the categorical columns
        """
        # NAME_CONTRACT_STATUS
        name_contract_dict = {'Approved': 0, 'Unused offer': 1, 'Canceled': 2, 'Refused': 3}
        self.df['NAME_CONTRACT_STATUS'] = self.df['NAME_CONTRACT_STATUS'].map(name_contract_dict)

        # NAME_YIELD_GROUP
        yield_group_dict = {'XNA': 0, 'low_action': 1, 'low_normal': 2, 'middle': 3, 'high': 4}
        self.df['NAME_YIELD_GROUP'] = self.df['NAME_YIELD_GROUP'].map(yield_group_dict)

        # FLAG_LAST_APPL_PER_CONTRACT
        appl_per_contract_dict = {'N': 0, 'Y': 1}
        self.df['FLAG_LAST_APPL_PER_CONTRACT'] = self.df['FLAG_LAST_APPL_PER_CONTRACT'].map(appl_per_contract_dict)

        remaining_categorical_columns = self.df.dtypes[self.df.dtypes == 'object'].index.tolist()
        for col in remaining_categorical_columns:
            encode_dict = dict([(i,j) for j, i in enumerate(self.df[col].unique(), 1)])
            self.df[col] = self.df[col].map(encode_dict)

        self.df['MISSING_VALUES_TOTAL_PREV'] = self.df.isna().sum(axis=1)
        self.df['AMT_CREDIT_GOODS_RATIO'] = self.df['AMT_CREDIT'] / (self.df['AMT_GOODS_PRICE'] + 1e-5)
        self.df['AMT_CREDIT_GOODS_DIFF'] = self.df['AMT_CREDIT'] - self.df['AMT_GOODS_PRICE']
        self.df['AMT_DECLINED'] = self.df['AMT_APPLICATION'] - self.df['AMT_CREDIT']
        self.df['AMT_CREDIT_APPLICATION_RATIO'] = self.df['AMT_APPLICATION'] / (self.df['AMT_CREDIT'] + 1e-5)
        self.df['CREDIT_DOWNPAYMENT_RATIO'] = self.df['AMT_DOWN_PAYMENT'] / (self.df['AMT_CREDIT'] + 1e-5)
        self.df['GOOD_DOWNPAYMENT_RATIO'] = self.df['AMT_DOWN_PAYMENT'] / (self.df['AMT_GOODS_PRICE'] + 1e-5)
        self.df['INTEREST_DOWNPAYMENT'] = self.df['RATE_DOWN_PAYMENT'] * self.df['AMT_DOWN_PAYMENT']
        self.df['INTEREST_CREDIT'] = self.df['AMT_CREDIT'] * self.df['RATE_INTEREST_PRIMARY']
        self.df['INTEREST_CREDIT_PRIVILEGED'] = self.df['AMT_CREDIT'] * self.df['RATE_INTEREST_PRIVILEGED']
        self.df['APPLICATION_AMT_TO_DECISION_RATIO'] = -self.df['AMT_APPLICATION'] / (self.df['DAYS_DECISION'] + 1e-5)
        self.df['AMT_APPLICATION_TO_SELLER_PLACE'] = self.df['AMT_APPLICATION'] / (self.df['SELLERPLACE_AREA'] + 1e-5)
        self.df['ESTIMATOR_AMT_ANNUITY'] = self.df['AMT_CREDIT'] / (self.df['CNT_PAYMENT'] + 1e-5)
        self.df['ESTIMATOR_AMT_GOODS_ANNUITY'] = self.df['AMT_GOODS_PRICE'] / (self.df['CNT_PAYMENT'] + 1e-5)
        self.df['DAYS_FIRST_LAST_DUE_DIFF'] = self.df['DAYS_LAST_DUE'] - self.df['DAYS_FIRST_DUE']
        self.df['AMT_CREDIT_HOUR_PROCESS_START'] = self.df['AMT_CREDIT'] * self.df['HOUR_APPR_PROCESS_START']
        self.df['AMT_CREDIT_NFLAG_LAST_APPL_DAY'] = self.df['AMT_CREDIT'] * self.df['NFLAG_LAST_APPL_IN_DAY']
        self.df['AMT_CREDIT_YIELD_GROUP'] = self.df['AMT_CREDIT'] * self.df['NAME_YIELD_GROUP']
        self.df['AMT_INTEREST'] = self.df['CNT_PAYMENT'] * self.df['AMT_ANNUITY'] - self.df['AMT_CREDIT']
        self.df['INTEREST_SHARE'] = self.df['AMT_INTEREST'] / (self.df['AMT_CREDIT'] + 1e-5)
        self.df['INTEREST_RATE'] = 2 * 12 * self.df['AMT_INTEREST'] / (self.df['AMT_CREDIT'] * (self.df['CNT_PAYMENT'] + 1))

    def aggregation(self):
        """Grouping by SK_ID_CURR"""
        aggregation_columns = {
            'MISSING_VALUES_TOTAL_PREV': ['sum'],
            'NAME_CONTRACT_STATUS': ['mean', 'last'],
            'AMT_ANNUITY': ['sum', 'mean', 'max'],
            'AMT_APPLICATION': ['sum', 'mean', 'max'],
            'AMT_CREDIT': ['sum', 'mean', 'max'],
            'AMT_DOWN_PAYMENT': ['sum', 'mean', 'max'],
            'AMT_GOODS_PRICE': ['sum', 'max', 'mean'],
            'WEEKDAY_APPR_PROCESS_START': ['max', 'min'],
            'HOUR_APPR_PROCESS_START': ['mean', 'max', 'min'],
            'NFLAG_LAST_APPL_IN_DAY': ['mean', 'sum'],
            'RATE_DOWN_PAYMENT': ['max', 'mean'],
            'RATE_INTEREST_PRIMARY': ['mean', 'max'],
            'RATE_INTEREST_PRIVILEGED': ['mean', 'max'],
            'NAME_CONTRACT_STATUS': ['mean', 'max', 'last', 'nunique'],
            'DAYS_DECISION': ['mean', 'max', 'min'],
            'NAME_CASH_LOAN_PURPOSE': ['nunique', 'last'],
            'NAME_PAYMENT_TYPE': ['nunique', 'last'],
            'NAME_CLIENT_TYPE' : ['nunique','last'],
            'NAME_GOODS_CATEGORY' : ['nunique','last'],
            'NAME_PORTFOLIO' : ['nunique','last'],
            'NAME_PRODUCT_TYPE' : ['nunique','last'],
            'CHANNEL_TYPE' : ['nunique','last'],
            'NAME_SELLER_INDUSTRY': ['nunique', 'last'],
            'SELLERPLACE_AREA': ['mean', 'max', 'min'],
            'CNT_PAYMENT': ['mean', 'max', 'sum'],
            'NAME_YIELD_GROUP': ['mean', 'max', 'min', 'last'],
            'PRODUCT_COMBINATION': ['last'],
            'DAYS_FIRST_DRAWING': ['mean', 'max'],
            'DAYS_FIRST_DUE': ['mean', 'max'],
            'DAYS_LAST_DUE_1ST_VERSION' : ['mean'],
            'DAYS_LAST_DUE' : ['mean'],
            'DAYS_TERMINATION' : ['mean','max'],
            'NFLAG_INSURED_ON_APPROVAL' : ['mean', 'sum'],
            'AMT_DECLINED': ['sum', 'mean', 'max'],
            'AMT_CREDIT_GOODS_RATIO': ['min', 'mean', 'max'],
            'AMT_CREDIT_GOODS_DIFF': ['max', 'sum', 'mean', 'min'],
            'AMT_CREDIT_APPLICATION_RATIO' : ['mean','min', 'max'],
            'CREDIT_DOWNPAYMENT_RATIO' : ['mean','max'],
            'GOOD_DOWNPAYMENT_RATIO' : ['mean','max'],
            'INTEREST_DOWNPAYMENT' : ['mean','sum','max'],
            'INTEREST_CREDIT' : ['mean','sum','max'],
            'INTEREST_CREDIT_PRIVILEGED' : ['mean','sum','max'],
            'APPLICATION_AMT_TO_DECISION_RATIO' : ['mean','min', 'max'],
            'AMT_APPLICATION_TO_SELLER_PLACE' : ['mean','max'],
            'ESTIMATOR_AMT_ANNUITY': ['max', 'sum', 'mean'],
            'ESTIMATOR_AMT_GOODS_ANNUITY': ['max', 'sum', 'mean'],
            'DAYS_FIRST_LAST_DUE_DIFF' : ['mean','max'],
            'AMT_CREDIT_HOUR_PROCESS_START' : ['mean','sum'],
            'AMT_CREDIT_NFLAG_LAST_APPL_DAY' : ['mean','max'],
            'AMT_CREDIT_YIELD_GROUP' : ['mean','sum','min'],
            'AMT_INTEREST' : ['mean','sum','max','min'],
            'INTEREST_SHARE' : ['mean','max','min'],
            'INTEREST_RATE' : ['mean','max','min']
        }
    
        last_3 = self.df.groupby('SK_ID_CURR').tail(5).groupby('SK_ID_CURR').agg(aggregation_columns)
        last_3.columns = ['_'.join(ele).upper() + '_LAST_5' for ele in last_3.columns]
        #grouping the previous applications over SK_ID_CURR while only taking the first 2 applications
        first_3 = self.df.groupby('SK_ID_CURR').head(2).groupby('SK_ID_CURR').agg(aggregation_columns)
        first_3.columns = ['_'.join(ele).upper() + '_FIRST_2' for ele in first_3.columns]
        #grouping the previous applications over SK_ID_CURR while taking all the applications into consideration
        group_all = self.df.groupby('SK_ID_CURR').agg(aggregation_columns)
        group_all.columns = ['_'.join(ele).upper() + '_ALL' for ele in group_all.columns]

        #merging all the applications
        previous_application_aggregated = last_3.merge(first_3, on = 'SK_ID_CURR', how = 'outer')
        previous_application_aggregated = previous_application_aggregated.merge(group_all, on = 'SK_ID_CURR', how = 'outer')

        return previous_application_aggregated

    def transform_dtype(self, data: pd.DataFrame):
         # Transform dtypes
        cate_cols = data.select_dtypes(include=['object', 'str']).columns
        data[cate_cols] = data[cate_cols].astype('category')
        return data
        

    def main(self):
        self.data_cleaning()
        self.feature_engineering()
        df = self.aggregation()
        df = self.transform_dtype(df)
        return df