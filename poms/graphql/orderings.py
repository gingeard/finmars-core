import strawberry
import strawberry_django

from poms.accounts.models import Account as AccountModel
from poms.accounts.models import AccountType as AccountTypeModel
from poms.counterparties.models import Counterparty as CounterpartyModel
from poms.counterparties.models import Responsible as ResponsibleModel
from poms.currencies.models import Currency as CurrencyModel
from poms.currencies.models import CurrencyHistory as CurrencyHistoryModel
from poms.instruments.models import Instrument as InstrumentModel
from poms.instruments.models import InstrumentType as InstrumentTypeModel
from poms.instruments.models import PriceHistory as PriceHistoryModel
from poms.instruments.models import PricingPolicy as PricingPolicyModel
from poms.portfolios.models import Portfolio as PortfolioModel
from poms.portfolios.models import PortfolioHistory as PortfolioHistoryModel
from poms.strategies.models import Strategy1 as Strategy1Model
from poms.strategies.models import Strategy2 as Strategy2Model
from poms.strategies.models import Strategy3 as Strategy3Model
from poms.transactions.models import ComplexTransaction as ComplexTransactionModel
from poms.transactions.models import Transaction as TransactionModel


@strawberry_django.order_type(AccountModel)
class AccountOrdering:
    id: strawberry.auto
    user_code: strawberry.auto
    name: strawberry.auto
    short_name: strawberry.auto
    created_at: strawberry.auto
    modified_at: strawberry.auto


@strawberry_django.order_type(AccountTypeModel)
class AccountTypeOrdering:
    id: strawberry.auto
    user_code: strawberry.auto
    name: strawberry.auto
    short_name: strawberry.auto
    created_at: strawberry.auto
    modified_at: strawberry.auto


@strawberry_django.order_type(CurrencyModel)
class CurrencyOrdering:
    id: strawberry.auto
    user_code: strawberry.auto
    name: strawberry.auto
    short_name: strawberry.auto
    created_at: strawberry.auto
    modified_at: strawberry.auto


@strawberry_django.order_type(CurrencyHistoryModel)
class CurrencyHistoryOrdering:
    id: strawberry.auto
    date: strawberry.auto
    created_at: strawberry.auto
    modified_at: strawberry.auto


@strawberry_django.order_type(PortfolioModel)
class PortfolioOrdering:
    id: strawberry.auto
    user_code: strawberry.auto
    name: strawberry.auto
    short_name: strawberry.auto
    created_at: strawberry.auto
    modified_at: strawberry.auto


@strawberry_django.order_type(PortfolioHistoryModel)
class PortfolioHistoryOrdering:
    id: strawberry.auto
    user_code: strawberry.auto
    date: strawberry.auto
    created_at: strawberry.auto
    modified_at: strawberry.auto


@strawberry_django.order_type(InstrumentTypeModel)
class InstrumentTypeOrdering:
    id: strawberry.auto
    user_code: strawberry.auto
    name: strawberry.auto
    short_name: strawberry.auto
    created_at: strawberry.auto
    modified_at: strawberry.auto


@strawberry_django.order_type(InstrumentModel)
class InstrumentOrdering:
    id: strawberry.auto
    user_code: strawberry.auto
    name: strawberry.auto
    short_name: strawberry.auto
    maturity_date: strawberry.auto
    created_at: strawberry.auto
    modified_at: strawberry.auto
    user_text_1: strawberry.auto
    user_text_2: strawberry.auto
    user_text_3: strawberry.auto


@strawberry_django.order_type(PricingPolicyModel)
class PricingPolicyOrdering:
    id: strawberry.auto
    user_code: strawberry.auto
    name: strawberry.auto
    short_name: strawberry.auto
    created_at: strawberry.auto
    modified_at: strawberry.auto


@strawberry_django.order_type(PriceHistoryModel)
class PriceHistoryOrdering:
    id: strawberry.auto
    date: strawberry.auto
    created_at: strawberry.auto
    modified_at: strawberry.auto


@strawberry_django.order_type(ResponsibleModel)
class ResponsibleOrdering:
    id: strawberry.auto
    user_code: strawberry.auto
    name: strawberry.auto
    short_name: strawberry.auto
    created_at: strawberry.auto
    modified_at: strawberry.auto


@strawberry_django.order_type(CounterpartyModel)
class CounterpartyOrdering:
    id: strawberry.auto
    user_code: strawberry.auto
    name: strawberry.auto
    short_name: strawberry.auto
    created_at: strawberry.auto
    modified_at: strawberry.auto


@strawberry_django.order_type(Strategy1Model)
class Strategy1Ordering:
    id: strawberry.auto
    user_code: strawberry.auto
    name: strawberry.auto
    short_name: strawberry.auto
    created_at: strawberry.auto
    modified_at: strawberry.auto


@strawberry_django.order_type(Strategy2Model)
class Strategy2Ordering:
    id: strawberry.auto
    user_code: strawberry.auto
    name: strawberry.auto
    short_name: strawberry.auto
    created_at: strawberry.auto
    modified_at: strawberry.auto


@strawberry_django.order_type(Strategy3Model)
class Strategy3Ordering:
    id: strawberry.auto
    user_code: strawberry.auto
    name: strawberry.auto
    short_name: strawberry.auto
    created_at: strawberry.auto
    modified_at: strawberry.auto


@strawberry_django.order_type(ComplexTransactionModel)
class ComplexTransactionOrdering:
    id: strawberry.auto
    date: strawberry.auto
    created_at: strawberry.auto
    modified_at: strawberry.auto
    text: strawberry.auto
    user_text_1: strawberry.auto
    user_text_2: strawberry.auto
    user_text_3: strawberry.auto
    user_text_4: strawberry.auto
    user_text_5: strawberry.auto
    user_text_6: strawberry.auto
    user_text_7: strawberry.auto
    user_text_8: strawberry.auto
    user_text_9: strawberry.auto
    user_text_10: strawberry.auto
    user_text_11: strawberry.auto
    user_text_12: strawberry.auto
    user_text_13: strawberry.auto
    user_text_14: strawberry.auto
    user_text_15: strawberry.auto
    user_text_16: strawberry.auto
    user_text_17: strawberry.auto
    user_text_18: strawberry.auto
    user_text_19: strawberry.auto
    user_text_20: strawberry.auto
    user_text_21: strawberry.auto
    user_text_22: strawberry.auto
    user_text_23: strawberry.auto
    user_text_24: strawberry.auto
    user_text_25: strawberry.auto
    user_text_26: strawberry.auto
    user_text_27: strawberry.auto
    user_text_28: strawberry.auto
    user_text_29: strawberry.auto
    user_text_30: strawberry.auto
    user_date_1: strawberry.auto
    user_date_2: strawberry.auto
    user_date_3: strawberry.auto
    user_date_4: strawberry.auto
    user_date_5: strawberry.auto
    user_date_6: strawberry.auto
    user_date_7: strawberry.auto
    user_date_8: strawberry.auto
    user_date_9: strawberry.auto
    user_date_10: strawberry.auto
    user_date_11: strawberry.auto
    user_date_12: strawberry.auto
    user_date_13: strawberry.auto
    user_date_14: strawberry.auto
    user_date_15: strawberry.auto
    user_date_16: strawberry.auto
    user_date_17: strawberry.auto
    user_date_18: strawberry.auto
    user_date_19: strawberry.auto
    user_date_20: strawberry.auto
    user_date_21: strawberry.auto
    user_date_22: strawberry.auto
    user_date_23: strawberry.auto
    user_date_24: strawberry.auto
    user_date_25: strawberry.auto
    user_date_26: strawberry.auto
    user_date_27: strawberry.auto
    user_date_28: strawberry.auto
    user_date_29: strawberry.auto
    user_date_30: strawberry.auto


@strawberry_django.order_type(TransactionModel)
class TransactionOrdering:
    id: strawberry.auto
    transaction_date: strawberry.auto
    accounting_date: strawberry.auto
    cash_date: strawberry.auto
    created_at: strawberry.auto
    modified_at: strawberry.auto
    notes: strawberry.auto
    user_text_1: strawberry.auto
    user_text_2: strawberry.auto
    user_text_3: strawberry.auto
    user_date_1: strawberry.auto
    user_date_2: strawberry.auto
    user_date_3: strawberry.auto
