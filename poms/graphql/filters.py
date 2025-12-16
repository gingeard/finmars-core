from datetime import date, datetime

import strawberry_django
from strawberry_django.filters import FilterLookup

from poms.accounts.models import Account as AccountModel
from poms.accounts.models import AccountType as AccountTypeModel
from poms.counterparties.models import Counterparty as CounterpartyModel
from poms.counterparties.models import Responsible as ResponsibleModel
from poms.currencies.models import Currency as CurrencyModel
from poms.currencies.models import CurrencyHistory as CurrencyHistoryModel
from poms.instruments.models import Country as CountryModel
from poms.instruments.models import Instrument as InstrumentModel
from poms.instruments.models import InstrumentType as InstrumentTypeModel
from poms.instruments.models import PriceHistory as PriceHistoryModel
from poms.portfolios.models import Portfolio as PortfolioModel
from poms.strategies.models import Strategy1 as Strategy1Model
from poms.strategies.models import Strategy2 as Strategy2Model
from poms.strategies.models import Strategy3 as Strategy3Model
from poms.transactions.models import ComplexTransaction as ComplexTransactionModel
from poms.transactions.models import Transaction as TransactionModel
from poms.transactions.models import TransactionClass as TransactionClassModel

BASE_FILTER_FIELDS = {
    "id": FilterLookup[int] | None,
    "user_code": FilterLookup[str] | None,
    "name": FilterLookup[str] | None,
    "notes": FilterLookup[str] | None,
    "public_name": FilterLookup[str] | None,
    "short_name": FilterLookup[str] | None,
    "created_at": FilterLookup[datetime] | None,
    "modified_at": FilterLookup[datetime] | None,
}


def make_filter(model, extra_fields: dict[str, object] | None = None):
    annotations = dict(BASE_FILTER_FIELDS)
    if extra_fields:
        annotations.update(extra_fields)

    # create a new class dynamically
    cls = type(
        f"{model.__name__}Filter",
        (),
        {"__annotations__": annotations},
    )

    # decorate it to bind to the model
    return strawberry_django.filter(model, lookups=True)(cls)


# SomeModel has extra field(s)
# SomeModelFilter = make_filter(
#     SomeModel,
#     extra_fields={
#         "category": FilterLookup[str] | None,
#         "is_active": FilterLookup[bool] | None,
#     },
# )


@strawberry_django.filter(TransactionClassModel, lookups=True)
class TransactionClassFilter:
    id: FilterLookup[int] | None = None
    name: FilterLookup[str] | None = None
    user_code: FilterLookup[str] | None = None
    short_name: FilterLookup[str] | None = None
    description: FilterLookup[str] | None = None


CountryFilter = make_filter(CountryModel)
AccountTypeFilter = make_filter(AccountTypeModel)
AccountFilter = make_filter(AccountModel, extra_fields={"type": AccountTypeFilter})


CurrencyFilter = make_filter(CurrencyModel, extra_fields={"country": CountryFilter | None})
CurrencyHistoryFilter = make_filter(
    CurrencyHistoryModel, extra_fields={"date": FilterLookup[date] | None, "currency": CurrencyFilter | None}
)

PortfolioFilter = make_filter(PortfolioModel)
InstrumentTypeFilter = make_filter(InstrumentTypeModel)
InstrumentFilter = make_filter(
    InstrumentModel,
    extra_fields={
        "maturity_date": FilterLookup[datetime] | None,
        "instrument_type": InstrumentTypeFilter | None,
        "pricing_currency": CurrencyFilter | None,
        "accrued_currency": CurrencyFilter | None,
        "country": CountryFilter | None,
    },
)

PriceHistoryFilter = make_filter(
    PriceHistoryModel, extra_fields={"date": FilterLookup[date] | None, "instrument": InstrumentFilter | None}
)

ResponsibleFilter = make_filter(ResponsibleModel)
CounterpartyFilter = make_filter(CounterpartyModel)

Strategy1Filter = make_filter(Strategy1Model)
Strategy2Filter = make_filter(Strategy2Model)
Strategy3Filter = make_filter(Strategy3Model)

ComplexTransactionFilter = make_filter(ComplexTransactionModel)

TransactionFilter = make_filter(
    TransactionModel,
    extra_fields={
        "transaction_date": FilterLookup[date] | None,
        "accounting_date": FilterLookup[date] | None,
        "cash_date": FilterLookup[date] | None,
        "transaction_code": FilterLookup[int] | None,
        "user_text_1": FilterLookup[str] | None,
        "user_text_2": FilterLookup[str] | None,
        "user_text_3": FilterLookup[str] | None,
        "user_number_1": FilterLookup[float] | None,
        "user_number_2": FilterLookup[float] | None,
        "user_number_3": FilterLookup[float] | None,
        "user_date_1": FilterLookup[date] | None,
        "user_date_2": FilterLookup[date] | None,
        "user_date_3": FilterLookup[date] | None,
        "complex_transaction": ComplexTransactionFilter | None,
        "instrument": InstrumentFilter | None,
        "linked_instrument": InstrumentFilter | None,
        "portfolio": PortfolioFilter | None,
        "transaction_currency": CurrencyFilter | None,
        "settlement_currency": CurrencyFilter | None,
        "responsible": ResponsibleFilter | None,
        "counterparty": CounterpartyFilter | None,
        "account_cash": AccountFilter | None,
        "account_position": AccountFilter | None,
        "account_interim": AccountFilter | None,
        "strategy1_cash": Strategy1Filter | None,
        "strategy1_position": Strategy1Filter | None,
        "strategy2_cash": Strategy2Filter | None,
        "strategy2_position": Strategy2Filter | None,
        "strategy3_cash": Strategy3Filter | None,
        "strategy3_position": Strategy3Filter | None,
        "transaction_class": TransactionClassFilter | None,
    },
)
