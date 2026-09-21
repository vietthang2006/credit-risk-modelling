from dataclasses import dataclass

import pandas as pd

from srcs.data_preparation.feature_builder import FeatureBuilder
from srcs.reduce_mem_dataset import reduce_mem_usage


@dataclass
class RawDataBundle:
    application: pd.DataFrame
    prev_application: pd.DataFrame
    bureau: pd.DataFrame
    bureau_balance: pd.DataFrame
    credit_card_balance: pd.DataFrame
    pos_cash_balance: pd.DataFrame
    instalments_payments: pd.DataFrame


@dataclass
class DataPipelineConfig:
    target_col: str = "TARGET"
    reduce_memory: bool = True


class DataPipeline:
    def __init__(self, config: DataPipelineConfig | None = None):
        self.config = config or DataPipelineConfig()

    def run(self, raw: RawDataBundle) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame] | pd.DataFrame:
        df = FeatureBuilder(
            application=raw.application,
            prev_application=raw.prev_application,
            bureau=raw.bureau,
            bureau_balance=raw.bureau_balance,
            credit_card_balance=raw.credit_card_balance,
            pos_cash_balance=raw.pos_cash_balance,
            instalments_payments=raw.instalments_payments,
        ).build()

        if self.config.reduce_memory:
            df = reduce_mem_usage(df)

        if self.config.target_col not in df.columns:
            return df

        y = df[self.config.target_col]
        X = df.drop(columns=[self.config.target_col])

        return X, y, df