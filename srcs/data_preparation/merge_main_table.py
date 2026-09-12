import pandas as pd

class MainTableMerger:

    def __init__(self, key: str = "SK_ID_CURR"):
        self.key = key

    def merge(self, application: pd.DataFrame, feature_tables: list[pd.DataFrame]) -> pd.DataFrame:

        main_table = application.copy()
        for feature_table in feature_tables:
            main_table = main_table.merge(feature_table, on=self.key, how="left")

        return main_table