import pandas as pd
import numpy as np

class InstallmentPaymentPrepare:

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def instalments_payments_preprocessing(self):
        """Data Preprocessing for instalments payments"""

        # Sorting by SK_ID_PREV, SK_ID_CURR and NUM_INSTALMENT_NUMBER
        self.df = self.df.sort_values(by=['SK_ID_CURR', 'SK_ID_PREV', 'NUM_INSTALMENT_NUMBER'], ascending=True)

        # Quality features for missing values
        self.df['MISSING_VALUES_TOTAL_INSTALMENT'] = self.df.isna().sum(axis=1)

    def instalments_payments_feature_engineering(self):
        self.df['DAYS_PAYMENT_RATIO'] = self.df['DAYS_INSTALMENT'] / (self.df['DAYS_ENTRY_PAYMENT'] + 1e-5)
        self.df['DAYS_PAYMENT_DIFF'] = self.df['DAYS_INSTALMENT'] - self.df['DAYS_ENTRY_PAYMENT']
        self.df['AMT_PAYMENT_RATIO'] = self.df['AMT_PAYMENT'] / (self.df['AMT_INSTALMENT'] + 1e-5)
        self.df['AMT_PAYMENT_DIFF'] = self.df['AMT_INSTALMENT'] - self.df['AMT_PAYMENT']
        self.df['EXP_DAYS_PAYMENT_RATIO'] = self.df.groupby('SK_ID_PREV')['DAYS_PAYMENT_RATIO'].transform(lambda x: x.ewm(alpha=0.5).mean())
        self.df['EXP_DAYS_PAYMENT_DIFF'] = self.df.groupby('SK_ID_PREV')['DAYS_PAYMENT_DIFF'].transform(lambda x: x.ewm(alpha=0.5).mean())
        self.df['EXP_AMT_PAYMENT_RATIO'] = self.df.groupby('SK_ID_PREV')['AMT_PAYMENT_RATIO'].transform(lambda x: x.ewm(alpha=0.5).mean())
        self.df['EXP_AMT_PAYMENT_DIFF'] = self.df.groupby('SK_ID_PREV')['AMT_PAYMENT_DIFF'].transform(lambda x: x.ewm(alpha=0.5).mean())

    def aggregation_prev_instalment(self):
        """
        Statistic grouping by SK_ID_PREV
        """

        overall_aggreagations = {
            'MISSING_VALUES_TOTAL_INSTALMENT': ['sum'],
            'NUM_INSTALMENT_VERSION': ['mean', 'sum'],
            'NUM_INSTALMENT_NUMBER': ['max'],
            'DAYS_INSTALMENT': ['max', 'min'],
            'DAYS_ENTRY_PAYMENT': ['max', 'min'],
            'AMT_INSTALMENT': ['mean', 'sum', 'max'],
            'AMT_PAYMENT': ['mean', 'sum', 'max'],
            'DAYS_PAYMENT_RATIO': ['max', 'min', 'mean'],
            'DAYS_PAYMENT_DIFF': ['max', 'min', 'mean'],
            'AMT_PAYMENT_RATIO': ['max', 'min', 'mean'],
            'AMT_PAYMENT_DIFF': ['max', 'min', 'mean'],
            'EXP_DAYS_PAYMENT_RATIO': ['last'],
            'EXP_DAYS_PAYMENT_DIFF': ['last'],
            'EXP_AMT_PAYMENT_RATIO': ['last'],
            'EXP_AMT_PAYMENT_DIFF': ['last'],
        }

        limited_period_aggregations = {
            'NUM_INSTALMENT_VERSION' : ['mean','sum'],
            'AMT_INSTALMENT' : ['mean', 'sum', 'max'],
            'AMT_PAYMENT' : ['mean', 'sum', 'max'],
            'DAYS_PAYMENT_RATIO' : ['mean', 'min','max'],
            'DAYS_PAYMENT_DIFF' : ['mean','min','max'],
            'AMT_PAYMENT_RATIO' : ['mean','min','max'],
            'AMT_PAYMENT_DIFF' : ['mean','min','max'],
            'EXP_DAYS_PAYMENT_RATIO' : ['last'],
            'EXP_DAYS_PAYMENT_DIFF' : ['last'],
            'EXP_AMT_PAYMENT_RATIO' : ['last'],
            'EXP_AMT_PAYMENT_DIFF' : ['last']
        }

        last_1_year = self.df[self.df['DAYS_INSTALMENT'] > -365].groupby('SK_ID_PREV').agg(limited_period_aggregations)
        last_1_year.columns = ['_'.join(i).upper() + '_LAST_1_YEAR' for i in last_1_year.columns]
        first_5_instalments = self.df.groupby('SK_ID_PREV', as_index=False).head(5).groupby('SK_ID_PREV').agg(limited_period_aggregations)
        first_5_instalments.columns = ['_'.join(i).upper() + '_FIRST_5_INSTALMENTS' for i in first_5_instalments.columns]
        overall = self.df.groupby(['SK_ID_PREV', 'SK_ID_CURR'], as_index=False).agg(overall_aggreagations)
        overall.columns = ['_'.join(i).upper() for i in overall.columns]
        overall.rename(columns={'SK_ID_PREV_': 'SK_ID_PREV', 'SK_ID_CURR_': 'SK_ID_CURR'}, inplace=True)

        # Merging 
        installments_payment_agg_prev = overall.merge(last_1_year, on='SK_ID_PREV', how='outer')
        installments_payment_agg_prev = installments_payment_agg_prev.merge(first_5_instalments, on='SK_ID_PREV', how='outer')

        return installments_payment_agg_prev

    def aggregation_curr_instalment(self, installments_payment_agg_prev):
        """Statistic grouping by SK_ID_CURR"""

        aggregations = {
            'MISSING_VALUES_TOTAL_INSTALMENT_SUM': ['sum'],
            'NUM_INSTALMENT_VERSION_MEAN': ['mean'],
            'NUM_INSTALMENT_VERSION_SUM': ['mean'],
            'NUM_INSTALMENT_NUMBER_MAX': ['mean', 'max', 'min'],
            'AMT_INSTALMENT_MEAN': ['mean', 'sum', 'max'],
            'AMT_INSTALMENT_SUM': ['mean', 'sum', 'max'],
            'AMT_INSTALMENT_MAX': ['mean'],
            'AMT_PAYMENT_MEAN': ['mean', 'sum', 'max'],
            'AMT_PAYMENT_SUM': ['mean', 'sum', 'max'],
            'AMT_PAYMENT_MAX': ['mean'],
            'DAYS_PAYMENT_RATIO_MAX': ['max', 'mean'],
            'DAYS_PAYMENT_RATIO_MIN': ['min', 'mean'],
            'DAYS_PAYMENT_RATIO_MEAN': ['max', 'min', 'mean'],
            'DAYS_PAYMENT_DIFF_MAX': ['max', 'mean'],
            'DAYS_PAYMENT_DIFF_MIN': ['min', 'mean'],
            'DAYS_PAYMENT_DIFF_MEAN': ['max', 'min', 'mean'],
            'AMT_PAYMENT_RATIO_MAX': ['max','mean'],
            'AMT_PAYMENT_RATIO_MEAN': ['max', 'min', 'mean'],
            'AMT_PAYMENT_RATIO_MIN': ['min', 'mean'],
            'AMT_PAYMENT_DIFF_MAX': ['max', 'mean'],
            'AMT_PAYMENT_DIFF_MEAN': ['max', 'min', 'mean'],
            'EXP_DAYS_PAYMENT_RATIO_LAST': ['mean'],
            'EXP_DAYS_PAYMENT_DIFF_LAST': ['mean'],
            'EXP_AMT_PAYMENT_RATIO_LAST': ['mean'],
            'EXP_AMT_PAYMENT_DIFF_LAST': ['mean']       
        }

        agg_group_main = installments_payment_agg_prev.groupby('SK_ID_CURR').agg(aggregations)
        agg_group_main.columns = ['_'.join(i).upper() for i in agg_group_main.columns]

        agg_remaining_cols = installments_payment_agg_prev.iloc[:, [1] + list(range(31,len(installments_payment_agg_prev.columns)))].groupby('SK_ID_CURR').mean()
        return agg_remaining_cols

    def main(self):
        self.instalments_payments_preprocessing()
        self.instalments_payments_feature_engineering()
        df = self.aggregation_prev_instalment()
        agg = self.aggregation_curr_instalment(df)
        return agg
