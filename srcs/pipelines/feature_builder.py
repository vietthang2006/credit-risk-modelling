from srcs.data_preparation.application import ApplicationPrepare
from srcs.data_preparation.previous_application import PreviousApplicationPrepare
from srcs.data_preparation.bureau_bureau_balance import BureauDataPrepare
from srcs.data_preparation.credit_card_balance import CreditCardBalancePrepare
from srcs.data_preparation.pos_cash_balance import POSCashBalancePrepare
from srcs.data_preparation.installments_payments import InstallmentPaymentPrepare
import pandas as pd
from srcs.data_preparation.merge_main_table import MainTableMerger
class FeatureBuilder:

    def __init__(
        self,
        application: pd.DataFrame,
        prev_application: pd.DataFrame,
        bureau: pd.DataFrame,
        bureau_balance: pd.DataFrame,
        credit_card_balance: pd.DataFrame,
        pos_cash_balance: pd.DataFrame,
        instalments_payments: pd.DataFrame,
    ):
        self.application = application
        self.prev_application = prev_application
        self.bureau = bureau
        self.bureau_balance = bureau_balance
        self.credit_card_balance = credit_card_balance
        self.pos_cash_balance = pos_cash_balance
        self.instalments_payments = instalments_payments

    def agg_application(self) -> pd.DataFrame:
        initiate = ApplicationPrepare(df=self.application)
        return initiate.main()

    def agg_prev_application(self) -> pd.DataFrame:
        initiate = PreviousApplicationPrepare(df=self.prev_application)
        return initiate.main()

    def agg_bureau_bureau_balance(self) -> pd.DataFrame:
        initiate = BureauDataPrepare(bureau=self.bureau,bureau_balance=self.bureau_balance,)
        return initiate.main()

    def agg_credit_card_balance(self) -> pd.DataFrame:
        initiate = CreditCardBalancePrepare(df=self.credit_card_balance)
        return initiate.main()

    def agg_pos_cash_balance(self) -> pd.DataFrame:
        initiate = POSCashBalancePrepare(df=self.pos_cash_balance)
        return initiate.main()

    def agg_installments_payments(self) -> pd.DataFrame:
        initiate = InstallmentPaymentPrepare(self.instalments_payments)
        return initiate.main()

    def build(self) -> pd.DataFrame:

        agg_application = self.agg_application()
        agg_prev_application = self.agg_prev_application()
        agg_bureau = self.agg_bureau_bureau_balance()
        agg_credit_card = self.agg_credit_card_balance()
        agg_pos_cash = self.agg_pos_cash_balance()
        agg_installments = self.agg_installments_payments()
        merger = MainTableMerger(key="SK_ID_CURR")

        main_table = merger.merge(
            application=agg_application,
            feature_tables=[
                agg_bureau,
                agg_prev_application,
                agg_credit_card,
                agg_pos_cash,
                agg_installments,
            ],
        )

        return main_table