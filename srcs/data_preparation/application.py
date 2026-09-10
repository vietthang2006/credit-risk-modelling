import pandas as pd
import numpy as np
from lightgbm import LGBMRegressor
from utils import cfg
from xgboost import XGBRegressor

class ApplicationPrepare:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def data_cleaning(self):
        """
        Function to clean the data, removing outlier/anomaly rows/entries
        """

        cols_flag_to_remove = ['FLAG_DOCUMENT_' + str(i) for i in [2,4,10,12,20]]
        self.df = self.df.drop(cols_flag_to_remove, axis=1)
        self.df['DAYS_BIRTH'] = -self.df['DAYS_BIRTH'] / 365.25
        self.df['DAYS_EMPLOYED'][self.df['DAYS_EMPLOYED'] == 365243] = np.nan
        self.df['DAYS_EMPLOYED'] = -self.df['DAYS_EMPLOYED'] / 365.25
        self.df['OBS_30_CNT_SOCIAL_CIRCLE'][self.df['OBS_30_CNT_SOCIAL_CIRCLE'] > 30] = np.nan
        self.df['OBS_60_CNT_SOCIAL_CIRCLE'][self.df['OBS_60_CNT_SOCIAL_CIRCLE'] > 30] = np.nan
        self.df = self.df[self.df['CODE_GENDER'] != 'XNA']
        categorical_cols = self.df.select_dtypes(include=['str', 'object']).columns.tolist()
        self.df[categorical_cols] = self.df[categorical_cols].fillna('XNA')
        self.df['REGION_RATING_CLIENT'] = self.df['REGION_RATING_CLIENT'].astype('object')
        self.df['REGION_RATING_CLIENT_W_CITY'] = self.df['REGION_RATING_CLIENT_W_CITY'].astype('object')
        self.df['MISSING_TOTAL'] = self.df.isna().sum(axis=1)

    def ext_source_prediction(self):
        """Predict the missing values of EXT_SOURCE features"""
        exclude_cols = {'EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3', 'SK_ID_CURR'}
        training_cols = [col for col in self.df.select_dtypes(exclude=['object', 'string', 'category']).columns if col not in exclude_cols]
        for col in ['EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3']:
            X_train = self.df.loc[self.df[col].notna(), training_cols]
            Y_train = self.df.loc[self.df[col].notna(), col]
            X_test = self.df.loc[self.df[col].isna(), training_cols]

            xgb = XGBRegressor(n_estimators=1000, max_depth=3, learning_rate=0.1, n_jobs=-1, random_state=59)
            xgb.fit(X_train, Y_train)
            self.df.loc[self.df[col].isna(), col] = xgb.predict(X_test)

            training_cols = training_cols + [col]

    def cnt_payment_prediction(self, df: pd.DataFrame, previous_application: pd.DataFrame = pd.read_csv(cfg.get_train('previous_application'))):
        """
        Function to predict the count payments on Current loans
        Using the previous applications data as a train set
        """
        train_data = previous_application[['AMT_CREDIT', 'AMT_ANNUITY', 'CNT_PAYMENT']].dropna()
        train_data['CREDIT_ANNUITY_RATIO'] = train_data['AMT_CREDIT'] / (train_data['AMT_ANNUITY'] + 1e-5)
        target_train = train_data.pop('CNT_PAYMENT')

        test_data = df[['AMT_CREDIT', 'AMT_ANNUITY']].fillna(0)
        test_data['CREDIT_ANNUITY_RATIO'] = test_data['AMT_CREDIT'] / (test_data['AMT_ANNUITY'] + 1e-5)

        lgbm = LGBMRegressor(
            max_depth=9,
            n_estimators=5000,
            n_jobs=-1,
            learning_rate=0.3,
            random_state=42
        )
        lgbm.fit(train_data, target_train)
        prediction = lgbm.predict(test_data)
        cnt_payment = pd.Series(
            np.asarray(prediction),
            index=test_data.index,
            name='CNT_PAYMENT'
        )

        return cnt_payment

    def numerical_engineering(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Function to create, transform features.
        """
        # Income, debt
        data['CREDIT_INCOME_RATIO'] = data['AMT_CREDIT'] / (data['AMT_INCOME_TOTAL'] + 1e-5)
        data['CREDIT_ANNUITY_RATIO'] = data['AMT_CREDIT'] / (data['AMT_ANNUITY'] + 1e-5)
        data['ANNUITY_INCOME_RATIO'] = data['AMT_ANNUITY'] / (data['AMT_INCOME_TOTAL'] + 1e-5)
        data['INCOME_ANNUITY_DIFF'] = data['AMT_INCOME_TOTAL'] - data['AMT_ANNUITY']
        data['CREDIT_GOODS_RATIO'] = data['AMT_CREDIT'] / (data['AMT_GOODS_PRICE'] + 1e-5)
        data['CREDIT_GOODS_RATIO'] = data['AMT_CREDIT'] - data['AMT_GOODS_PRICE']
        data['GOODS_INCOME_RATIO'] = data['AMT_GOODS_PRICE'] / (data['AMT_INCOME_TOTAL'] + 1e-5)
        data['INCOME_EXT_RATIO'] = data['AMT_INCOME_TOTAL'] / (data['EXT_SOURCE_3'] + 1e-5)
        data['CREDIT_EXT_RATIO'] = data['AMT_CREDIT'] / (data['EXT_SOURCE_3'] + 1e-5)

        # Age ratio, diffs
        data['AGE_EMPLOYED_DIFF'] = data['DAYS_BIRTH'] - data['DAYS_EMPLOYED']
        data['EMPLOYED_TO_AGE_RATIO'] = data['DAYS_EMPLOYED'] / (data['DAYS_BIRTH'] + 1e-5)

        # car ratio
        data['CAR_EMPLOYED_DIFF'] = data['OWN_CAR_AGE'] - data['DAYS_EMPLOYED']
        data['CAR_EMPLOYED_RATIO'] = data['OWN_CAR_AGE'] / (data['DAYS_EMPLOYED'] + 1e-5)
        data['CAR_AGE_DIFF'] = data['DAYS_BIRTH'] - data['OWN_CAR_AGE']
        data['CAR_AGE_RATIO'] = data['OWN_CAR_AGE'] / (data['DAYS_BIRTH'] + 1e-5)

        # Flag count
        data['FLAG_SUM'] = data['FLAG_MOBIL'] + data['FLAG_EMP_PHONE'] + data['FLAG_WORK_PHONE'] + data['FLAG_CONT_MOBILE'] + data['FLAG_PHONE'] + data['FLAG_EMAIL']
        data['HOUR_PROCESS_CREDIT_MUL'] = data['AMT_CREDIT'] * data['HOUR_APPR_PROCESS_START']
        data['CNT_NON_CHILDREN'] = data['CNT_FAM_MEMBERS'] - data['CNT_CHILDREN']
        data['CHILDREN_INCOME_RATIO'] = data['CNT_CHILDREN'] / (data['AMT_INCOME_TOTAL'] + 1e-5)
        data['PER_CAPITA_INCOME'] = data['AMT_INCOME_TOTAL'] / (data['CNT_FAM_MEMBERS'] + 1)
    
        # Region
        data['REGION_RATING_INCOME'] = (data['REGION_RATING_CLIENT'] + data['REGION_RATING_CLIENT_W_CITY']) * data['AMT_INCOME_TOTAL'] / 2
        data['REGION_RATING_MAX'] = [max(i,j) for i, j in zip(data['REGION_RATING_CLIENT'], data['REGION_RATING_CLIENT_W_CITY'])]
        data['REGION_RATING_MIN'] = [min(i,j) for i, j in zip(data['REGION_RATING_CLIENT'], data['REGION_RATING_CLIENT_W_CITY'])]
        data['REGION_RATING_MEAN'] = (data['REGION_RATING_CLIENT'] + data['REGION_RATING_CLIENT_W_CITY']) / 2
        data['REGION_RATING_MUL'] = data['REGION_RATING_CLIENT'] * data['REGION_RATING_CLIENT_W_CITY']
        data['REGION_RATING_DIFF'] = data['REGION_RATING_CLIENT_W_CITY'] - data['REGION_RATING_CLIENT']
        region_cols = ['REG_REGION_NOT_LIVE_REGION', 'REG_REGION_NOT_WORK_REGION', 'LIVE_REGION_NOT_WORK_REGION']
        city_cols = ['REG_CITY_NOT_LIVE_CITY', 'REG_CITY_NOT_WORK_CITY', 'LIVE_CITY_NOT_WORK_CITY']
        data['REGION_MISMATCH_COUNT'] = data[region_cols].sum(axis=1)
        data['CITY_MISMATCH_COUNT'] = data[city_cols].sum(axis=1)

        # EXT_SOURCE
        data['EXT_SOURCE_MEAN'] = (data['EXT_SOURCE_1'] + data['EXT_SOURCE_2'] + data['EXT_SOURCE_3']) / 3
        data['EXT_SOURCE_VAR'] = [np.var([ele1,ele2,ele3]) for ele1, ele2, ele3 in zip(data['EXT_SOURCE_1'], data['EXT_SOURCE_2'], data['EXT_SOURCE_3'])]
        data['EXT_SOURCE_MAX'] = [max(ele1,ele2,ele3) for ele1, ele2, ele3 in zip(data['EXT_SOURCE_1'], data['EXT_SOURCE_2'], data['EXT_SOURCE_3'])]
        data['EXT_SOURCE_MIN'] = [min(ele1,ele2,ele3) for ele1, ele2, ele3 in zip(data['EXT_SOURCE_1'], data['EXT_SOURCE_2'], data['EXT_SOURCE_3'])]
        data['EXT_SOURCE_MUL_SQRT'] = np.sqrt(data['EXT_SOURCE_1'] * data['EXT_SOURCE_2'] * data['EXT_SOURCE_3'])
        data['WEIGHTED_EXT_SOURCE'] = data['EXT_SOURCE_1'] * 2 + data['EXT_SOURCE_2'] * 3 + data['EXT_SOURCE_3'] * 3
        data['EXT_SOURCE_MISSING_COUNT'] = data[['EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3']].isna().sum(axis=1)  

        # Apartment features
        data['APARTMENTS_SUM_AVG'] = data['APARTMENTS_AVG'] + data['BASEMENTAREA_AVG'] + data['YEARS_BEGINEXPLUATATION_AVG'] + data[
                                    'YEARS_BUILD_AVG'] + data['COMMONAREA_AVG'] + data['ELEVATORS_AVG'] + data['ENTRANCES_AVG'] + data[
                                    'FLOORSMAX_AVG'] + data['FLOORSMIN_AVG'] + data['LANDAREA_AVG'] + data['LIVINGAPARTMENTS_AVG'] + data[
                                    'LIVINGAREA_AVG'] + data['NONLIVINGAPARTMENTS_AVG'] + data['NONLIVINGAREA_AVG']

        data['APARTMENTS_SUM_MODE'] = data['APARTMENTS_MODE'] + data['BASEMENTAREA_MODE'] + data['YEARS_BEGINEXPLUATATION_MODE'] + data[
                                    'YEARS_BUILD_MODE'] + data['COMMONAREA_MODE'] + data['ELEVATORS_MODE'] + data['ENTRANCES_MODE'] + data[
                                    'FLOORSMAX_MODE'] + data['FLOORSMIN_MODE'] + data['LANDAREA_MODE'] + data['LIVINGAPARTMENTS_MODE'] + data[
                                    'LIVINGAREA_MODE'] + data['NONLIVINGAPARTMENTS_MODE'] + data['NONLIVINGAREA_MODE'] + data['TOTALAREA_MODE']

        data['APARTMENTS_SUM_MEDI'] = data['APARTMENTS_MEDI'] + data['BASEMENTAREA_MEDI'] + data['YEARS_BEGINEXPLUATATION_MEDI'] + data[
                                    'YEARS_BUILD_MEDI'] + data['COMMONAREA_MEDI'] + data['ELEVATORS_MEDI'] + data['ENTRANCES_MEDI'] + data[
                                    'FLOORSMAX_MEDI'] + data['FLOORSMIN_MEDI'] + data['LANDAREA_MEDI'] + data['LIVINGAPARTMENTS_MEDI'] + data[
                                    'LIVINGAREA_MEDI'] + data['NONLIVINGAPARTMENTS_MEDI'] + data['NONLIVINGAREA_MEDI']
        data['INCOME_APARTMENT_AVG_MUL'] = data['APARTMENTS_SUM_AVG'] * data['AMT_INCOME_TOTAL']
        data['INCOME_APARTMENT_MODE_MUL'] = data['APARTMENTS_SUM_MODE'] * data['AMT_INCOME_TOTAL']
        data['INCOME_APARTMENT_MEDI_MUL'] = data['APARTMENTS_SUM_MEDI'] * data['AMT_INCOME_TOTAL']

        # OBS
        data['OBS_30_60_SUM'] = data['OBS_30_CNT_SOCIAL_CIRCLE'] + data['OBS_60_CNT_SOCIAL_CIRCLE']
        data['DEF_30_60_SUM'] = data['DEF_30_CNT_SOCIAL_CIRCLE'] + data['DEF_60_CNT_SOCIAL_CIRCLE']
        data['SOCIAL_30_DEFAULT_RATE'] = data['DEF_30_CNT_SOCIAL_CIRCLE'] / data['OBS_30_CNT_SOCIAL_CIRCLE']
        data['SOCIAL_60_DEFAULT_RATE'] = data['DEF_60_CNT_SOCIAL_CIRCLE'] / data['OBS_60_CNT_SOCIAL_CIRCLE']
        data['OBS_30_CREDIT_RATIO'] = data['AMT_CREDIT'] / (data['OBS_30_CNT_SOCIAL_CIRCLE'] + 1e-5)
        data['OBS_60_CREDIT_RATIO'] = data['AMT_CREDIT'] / (data['OBS_60_CNT_SOCIAL_CIRCLE'] + 1e-5)
        data['DEF_30_CREDIT_RATIO'] = data['AMT_CREDIT'] / (data['DEF_30_CNT_SOCIAL_CIRCLE'] + 1e-5)
        data['DEF_60_CREDIT_RATIO'] = data['AMT_CREDIT'] / (data['DEF_60_CNT_SOCIAL_CIRCLE'] + 1e-5)

        # FLAG_DOCUMENT
        data['SUM_FLAGS_DOCUMENTS'] = data['FLAG_DOCUMENT_3'] + data['FLAG_DOCUMENT_5'] + data['FLAG_DOCUMENT_6']  + data[
                                    'FLAG_DOCUMENT_7'] + data['FLAG_DOCUMENT_8'] + data['FLAG_DOCUMENT_9'] + data[
                                    'FLAG_DOCUMENT_11'] + data['FLAG_DOCUMENT_13'] + data['FLAG_DOCUMENT_14'] + data[
                                    'FLAG_DOCUMENT_15'] + data['FLAG_DOCUMENT_16'] + data['FLAG_DOCUMENT_17'] + data[
                                    'FLAG_DOCUMENT_18'] + data['FLAG_DOCUMENT_19'] + data['FLAG_DOCUMENT_21']

        # Detail change
        data['DAYS_DETAILS_CHANGE_MUL'] = data['DAYS_LAST_PHONE_CHANGE'] * data['DAYS_REGISTRATION'] * data['DAYS_ID_PUBLISH']
        data['DAYS_DETAILS_CHANGE_SUM'] = data['DAYS_LAST_PHONE_CHANGE'] + data['DAYS_REGISTRATION'] + data['DAYS_ID_PUBLISH']

        # Enquires
        ENQ_COLUMNS = [f'AMT_REQ_CREDIT_BUREAU_{i}' for i in ['HOUR', 'DAY', 'WEEK', 'MON', 'QRT', 'YEAR']]
        data['AMT_ENQ_SUM'] = data[ENQ_COLUMNS].sum(axis=1)
        data['AMT_ENQ_SUM_CREDIT_RATIO'] = data['AMT_ENQ_SUM'] / (data['AMT_CREDIT'] + 1e-5)
        data['INQUIRY_1D'] = data['AMT_REQ_CREDIT_BUREAU_HOUR'] + data['AMT_REQ_CREDIT_BUREAU_DAY']
        data['INQUIRY_1W'] = data['INQUIRY_1D'] + data['AMT_REQ_CREDIT_BUREAU_WEEK']
        data['INQUIRY_1M'] = data['INQUIRY_1W'] + data['AMT_REQ_CREDIT_BUREAU_MON']
        data['INQUIRY_3M'] = data['INQUIRY_1M'] + data['AMT_REQ_CREDIT_BUREAU_QRT']
        data['INQUIRY_1Y'] = data['INQUIRY_3M'] + data['AMT_REQ_CREDIT_BUREAU_YEAR']
        data['HAS_RECENT_INQUIRY'] = (data['INQUIRY_1M'] > 0).astype(int)
        data['INQUIRY_RECENT_INTENSITY'] = data['INQUIRY_1M'] / (data['INQUIRY_1Y'] + 1)

        # Expected interest
        cnt_payment = self.cnt_payment_prediction(data)
        data['EXPECTED_CNT_PAYMENT'] = cnt_payment
        data['EXPECTED_INTEREST'] = data['AMT_ANNUITY'] * data['EXPECTED_CNT_PAYMENT']
        data['EXPECTED_INTEREST_SHARE'] = data['EXPECTED_INTEREST'] / (data['AMT_CREDIT'] + 1e-5)
        data['EXPECTED_INTEREST_RATE'] = 2 * 12 * data['EXPECTED_INTEREST'] / (data['AMT_CREDIT'] * (data['EXPECTED_CNT_PAYMENT'] + 1))

        return data
    
    def categorical_interaction_features(self, data: pd.DataFrame):
        """Function to creat features based on some categorical features grouping"""
        columns_to_aggregate_on = [
            ['NAME_CONTRACT_TYPE', 'NAME_INCOME_TYPE', 'OCCUPATION_TYPE'],
            ['CODE_GENDER', 'NAME_FAMILY_STATUS', 'NAME_INCOME_TYPE'],
            ['FLAG_OWN_CAR', 'FLAG_OWN_REALTY', 'NAME_INCOME_TYPE'],
            ['NAME_EDUCATION_TYPE', 'NAME_INCOME_TYPE', 'OCCUPATION_TYPE'],
            ['OCCUPATION_TYPE', 'ORGANIZATION_TYPE'],
            ['CODE_GENDER', 'FLAG_OWN_CAR', 'FLAG_OWN_REALTY']
        ]

        aggregations = {
            'AMT_ANNUITY': ['mean', 'max', 'min'],
            'ANNUITY_INCOME_RATIO': ['mean', 'max', 'min'],
            'AGE_EMPLOYED_DIFF': ['mean', 'min'],
            'AMT_INCOME_TOTAL': ['mean', 'max', 'min'],
            'APARTMENTS_SUM_AVG' : ['mean','max','min'],
            'APARTMENTS_SUM_MEDI' : ['mean','max','min'],
            'EXT_SOURCE_MEAN' : ['mean','max','min'],
            'EXT_SOURCE_1' : ['mean','max','min'],
            'EXT_SOURCE_2' : ['mean','max','min'],
            'EXT_SOURCE_3' : ['mean','max','min']
        }

        for group in columns_to_aggregate_on:
            grouped_interactions = data.groupby(group).agg(aggregations)
            grouped_interactions.columns = ['_'.join(i).upper() + '_AGG_' + '_'.join(group) for i in grouped_interactions.columns]
            data = data.join(grouped_interactions, on=group)

        return data

    def transform(self):
        cate_cols = self.df.select_dtypes(include=['str', 'object']).columns 
        self.df[cate_cols] = self.df[cate_cols].astype('category')

    def main(self):
        self.data_cleaning()
        self.ext_source_prediction()
        self.df = self.numerical_engineering(self.df)
        self.df = self.categorical_interaction_features(self.df)
        self.transform()
        return self.df