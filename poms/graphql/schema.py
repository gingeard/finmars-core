from __future__ import annotations

import dataclasses
import logging
from datetime import date
from typing import Any, TypeVar

import strawberry
import strawberry_django
from strawberry.schema.config import StrawberryConfig

from poms.accounts.models import Account as AccountModel
from poms.accounts.models import AccountType as AccountTypeModel
from poms.counterparties.models import Counterparty as CounterpartyModel
from poms.counterparties.models import Responsible as ResponsibleModel
from poms.currencies.models import Currency as CurrencyModel
from poms.currencies.models import CurrencyHistory as CurrencyHistoryModel
from poms.graphql.filters import (
    AccountFilter,
    AccountTypeFilter,
    ComplexTransactionFilter,
    CounterpartyFilter,
    CurrencyFilter,
    CurrencyHistoryFilter,
    InstrumentFilter,
    InstrumentTypeFilter,
    PortfolioFilter,
    PortfolioHistoryFilter,
    PriceHistoryFilter,
    PricingPolicyFilter,
    ResponsibleFilter,
    Strategy1Filter,
    Strategy2Filter,
    Strategy3Filter,
    TransactionFilter,
)
from poms.graphql.orderings import (
    AccountOrdering,
    AccountTypeOrdering,
    ComplexTransactionOrdering,
    CounterpartyOrdering,
    CurrencyHistoryOrdering,
    CurrencyOrdering,
    InstrumentOrdering,
    InstrumentTypeOrdering,
    PortfolioHistoryOrdering,
    PortfolioOrdering,
    PriceHistoryOrdering,
    PricingPolicyOrdering,
    ResponsibleOrdering,
    Strategy1Ordering,
    Strategy2Ordering,
    Strategy3Ordering,
    TransactionOrdering,
)
from poms.instruments.models import CostMethod as CostMethodModel
from poms.instruments.models import Country as CountryModel
from poms.instruments.models import Instrument as InstrumentModel
from poms.instruments.models import InstrumentType as InstrumentTypeModel
from poms.instruments.models import PriceHistory as PriceHistoryModel
from poms.instruments.models import PricingPolicy as PricingPolicyModel
from poms.portfolios.models import Portfolio as PortfolioModel
from poms.portfolios.models import PortfolioBundle as PortfolioBundleModel
from poms.portfolios.models import PortfolioHistory as PortfolioHistoryModel
from poms.portfolios.models import PortfolioRegister as PortfolioRegisterModel
from poms.reports.common import PerformanceReport as PerformanceReportModel
from poms.reports.common import Report as ReportModel
from poms.reports.common import TransactionReport as TransactionReportModel
from poms.reports.serializers_helpers import (
    serialize_balance_report_item,
    serialize_pl_report_item,
    serialize_price_checker_item,
    serialize_transaction_report_item,
)
from poms.reports.sql_builders.balance import BalanceReportBuilderSql
from poms.reports.sql_builders.pl import PLReportBuilderSql
from poms.reports.sql_builders.price_checkers import PriceHistoryCheckerSql
from poms.reports.sql_builders.transaction import TransactionReportBuilderSql
from poms.strategies.models import Strategy1 as Strategy1Model
from poms.strategies.models import Strategy2 as Strategy2Model
from poms.strategies.models import Strategy3 as Strategy3Model
from poms.transactions.models import ComplexTransaction as ComplexTransactionModel
from poms.transactions.models import Transaction as TransactionModel
from poms.transactions.models import TransactionClass as TransactionClassModel
from poms.users.models import Member as MemberModel

_l = logging.getLogger("poms.graphql")

T = TypeVar("T")

# Put here fields you NEVER want to expose (internal/state/provenance/etc)
COMMON_EXCLUDE = [
    # examples, keep/remove as you wish
    "error_message",
    "procedure_modified_datetime",
    # add any provenance/state fields from your mixins if you have them
]


# Small helper: "all model fields except blacklist"
def gql_type(model):
    return strawberry_django.type(
        model,
        fields="__all__",
        exclude=COMMON_EXCLUDE,
        pagination=True,  # makes list relations accept pagination args
    )


def from_dict(cls: type[T], data: dict[str, Any]) -> T:
    # keeps only fields declared in the strawberry/dataclass type
    allowed = {f.name for f in dataclasses.fields(cls)}
    filtered = {k: v for k, v in data.items() if k in allowed}
    return cls(**filtered)


# --- Types (minimal, no duplication) ---


@strawberry_django.type(MemberModel, fields="__all__")
class Member:
    pass


@strawberry_django.type(CountryModel, fields="__all__")
class Country:
    pass


@strawberry_django.type(TransactionClassModel)
class TransactionClass:
    id: int
    user_code: str
    name: str
    short_name: str
    description: str


@strawberry_django.type(AccountTypeModel, fields="__all__")
class AccountType:
    owner: Member | None


@strawberry_django.type(AccountModel, fields="__all__")
class Account:
    owner: Member | None
    type: AccountType | None


@strawberry_django.type(PricingPolicyModel, fields="__all__")
class PricingPolicy:
    owner: Member | None


@strawberry_django.type(CurrencyModel, fields="__all__")
class Currency:
    owner: Member | None
    country: Country | None


@strawberry_django.type(CurrencyHistoryModel, fields="__all__")
class CurrencyHistory:
    owner: Member | None
    currency: Currency | None
    pricing_policy: PricingPolicy | None


@strawberry_django.type(PortfolioModel, fields="__all__")
class Portfolio:
    owner: Member | None


@strawberry_django.type(PortfolioHistoryModel, fields="__all__")
class PortfolioHistory:
    owner: Member | None
    portfolio: Portfolio | None
    currency: Currency | None
    pricing_policy: PricingPolicy | None


@strawberry_django.type(InstrumentTypeModel, fields="__all__")
class InstrumentType:
    owner: Member | None


@strawberry_django.type(InstrumentModel, fields="__all__")
class Instrument:
    owner: Member | None
    instrument_type: InstrumentType | None
    pricing_currency: Currency | None
    accrued_currency: Currency | None
    country: Country | None


@strawberry_django.type(PriceHistoryModel, fields="__all__")
class PriceHistory:
    owner: Member | None
    instrument: Instrument | None
    pricing_policy: PricingPolicy | None


@strawberry_django.type(ResponsibleModel, fields="__all__")
class Responsible:
    owner: Member | None


@strawberry_django.type(CounterpartyModel, fields="__all__")
class Counterparty:
    owner: Member | None


@strawberry_django.type(Strategy1Model, fields="__all__")
class Strategy1:
    owner: Member | None


@strawberry_django.type(Strategy2Model, fields="__all__")
class Strategy2:
    owner: Member | None


@strawberry_django.type(Strategy3Model, fields="__all__")
class Strategy3:
    owner: Member | None


@strawberry_django.type(ComplexTransactionModel, fields="__all__")
class ComplexTransaction:
    owner: Member | None


@strawberry_django.type(TransactionModel, fields="__all__")
class Transaction:
    owner: Member | None
    complex_transaction: ComplexTransaction | None

    instrument: Instrument | None
    linked_instrument: Instrument | None
    allocation_balance: Instrument | None
    allocation_pl: Instrument | None

    portfolio: Portfolio | None

    transaction_currency: Currency | None
    settlement_currency: Currency | None

    responsible: Responsible | None
    counterparty: Counterparty | None

    account_cash: Account | None
    account_position: Account | None
    account_interim: Account | None

    strategy1_cash: Strategy1 | None
    strategy1_position: Strategy1 | None

    strategy2_cash: Strategy2 | None
    strategy2_position: Strategy2 | None

    strategy3_cash: Strategy3 | None
    strategy3_position: Strategy3 | None

    transaction_class: TransactionClass | None


# BALANCE REPORT STARTS


@strawberry.input
class BalanceReportInput:
    report_date: date
    report_currency: str = "USD"

    pricing_policy: str | None = None
    calculate_pl: bool = False
    cost_method: str = "avco"  # avco or fifo
    expression_iterations_count: int = 1
    custom_fields_to_calculate: str = ""
    calculation_group: str = "portfolio.id"

    portfolios: list[str] | None = None
    accounts: list[str] | None = None
    strategies1: list[str] | None = None
    strategies2: list[str] | None = None
    strategies3: list[str] | None = None

    portfolio_mode: str = "independent"
    account_mode: str = "independent"
    strategy1_mode: str = "independent"
    strategy2_mode: str = "independent"
    strategy3_mode: str = "independent"


@strawberry.type
class BalanceReportItem:
    id: str
    name: str
    short_name: str
    user_code: str
    portfolio: int
    item_type: int
    item_type_name: str
    instrument: int | None
    currency: int | None
    pricing_currency: int | None
    exposure_currency: int | None
    allocation: int | None
    instrument_pricing_currency_fx_rate: float
    instrument_accrued_currency_fx_rate: float
    instrument_principal_price: float
    instrument_accrued_price: float
    instrument_factor: float
    instrument_ytm: float
    daily_price_change: float
    account: int | None
    strategy1: int | None
    strategy2: int | None
    strategy3: int | None
    fx_rate: float
    position_size: float
    nominal_position_size: float
    market_value: float | None
    market_value_loc: float | None
    exposure: float | None
    exposure_loc: float | None
    ytm: float
    ytm_at_cost: float
    modified_duration: float
    return_annually: float
    return_annually_fixed: float
    position_return: float
    position_return_loc: float
    net_position_return: float
    net_position_return_loc: float
    position_return_fixed: float
    position_return_fixed_loc: float
    net_position_return_fixed: float
    net_position_return_fixed_loc: float
    net_cost_price: float
    net_cost_price_loc: float
    gross_cost_price: float
    gross_cost_price_loc: float
    principal_invested: float
    principal_invested_loc: float
    amount_invested: float
    amount_invested_loc: float
    principal_invested_fixed: float
    principal_invested_fixed_loc: float
    amount_invested_fixed: float
    amount_invested_fixed_loc: float
    time_invested: float
    principal: float
    carry: float
    overheads: float
    total: float
    principal_fx: float
    carry_fx: float
    overheads_fx: float
    total_fx: float
    principal_fixed: float
    carry_fixed: float
    overheads_fixed: float
    total_fixed: float
    principal_loc: float
    carry_loc: float
    overheads_loc: float
    total_loc: float
    principal_fx_loc: float
    carry_fx_loc: float
    overheads_fx_loc: float
    total_fx_loc: float
    principal_fixed_loc: float
    carry_fixed_loc: float
    overheads_fixed_loc: float
    total_fixed_loc: float


@strawberry.type
class BalanceReport:
    items: list[BalanceReportItem]


@strawberry.field
def balance_report(
    self,
    info,
    input: BalanceReportInput,
    limit: int = 50,
    offset: int = 0,
) -> BalanceReport:
    user = info.context.request.user

    report_currency = CurrencyModel.objects.get(user_code=input.report_currency)
    pricing_policy = PricingPolicyModel.objects.get(user_code=input.pricing_policy)

    portfolios = []

    if input.portfolios:
        portfolios = PortfolioModel.objects.filter(user_code__in=input.portfolios)

    accounts = []

    if input.accounts:
        accounts = AccountModel.objects.filter(user_code__in=input.accounts)

    strategies1 = []

    if input.strategies1:
        strategies1 = Strategy1Model.objects.filter(user_code__in=input.strategies1)

    strategies2 = []

    if input.strategies2:
        strategies2 = Strategy2Model.objects.filter(user_code__in=input.strategies2)

    strategies3 = []

    if input.strategies3:
        strategies3 = Strategy3Model.objects.filter(user_code__in=input.strategies3)

    cost_method = CostMethodModel.objects.get(user_code="avco")

    if input.cost_method == "fifo":
        cost_method = CostMethodModel.objects.get(user_code="fifo")

    portfolio_mode = 1

    if input.portfolio_mode == "ignore":
        portfolio_mode = 0

    account_mode = 1

    if input.account_mode == "ignore":
        account_mode = 0

    strategy1_mode = 1

    if input.strategy1_mode == "ignore":
        strategy1_mode = 0

    strategy2_mode = 1

    if input.strategy2_mode == "ignore":
        strategy2_mode = 0

    strategy3_mode = 1

    if input.strategy3_mode == "ignore":
        strategy3_mode = 0

    report = ReportModel(
        master_user=user.master_user,
        member=user.member,
        calculate_pl=input.calculate_pl,
        cost_method=cost_method,
        custom_fields_to_calculate=input.custom_fields_to_calculate,
        calculation_group=input.calculation_group,
        report_date=input.report_date,
        pricing_policy=pricing_policy,
        report_currency=report_currency,
        portfolio_mode=portfolio_mode,
        account_mode=account_mode,
        strategy1_mode=strategy1_mode,
        strategy2_mode=strategy2_mode,
        strategy3_mode=strategy3_mode,
        portfolios=portfolios,
        accounts=accounts,
        strategies1=strategies1,
        strategies2=strategies2,
        strategies3=strategies3,
    )

    builder = BalanceReportBuilderSql(report)
    report = builder.build_balance_sync()

    items = []

    for item in report.items:
        items.append(serialize_balance_report_item(item))

    # _l.info('report.items %s' % items[0])

    # 3) map result to GraphQL types
    return BalanceReport(
        items=[BalanceReportItem(**row) for row in items],
    )


# PL REPORT STARTS


@strawberry.input
class PLReportInput:
    pl_first_date: date | None = None
    report_date: date
    report_currency: str = "USD"
    period_type: str | None = None  # daily, mtd, qtd, ytd, inception

    pricing_policy: str | None = None
    calculate_pl: bool = False
    cost_method: str = "avco"  # avco or fifo
    expression_iterations_count: int = 1
    custom_fields_to_calculate: str = ""
    calculation_group: str = "portfolio.id"

    portfolios: list[str] | None = None
    accounts: list[str] | None = None
    strategies1: list[str] | None = None
    strategies2: list[str] | None = None
    strategies3: list[str] | None = None

    portfolio_mode: str = "independent"
    account_mode: str = "independent"
    strategy1_mode: str = "independent"
    strategy2_mode: str = "independent"
    strategy3_mode: str = "independent"


@strawberry.type
class PLReportItem:
    id: str
    name: str
    short_name: str
    user_code: str
    portfolio: int
    item_type: int
    item_type_name: str
    item_group: str | None = None
    item_group_code: str | None = None
    item_group_name: str | None = None
    instrument: int | None = None
    currency: int | None = None
    pricing_currency: int | None = None
    exposure_currency: int | None = None
    allocation: int | None = None
    instrument_pricing_currency_fx_rate: float | None = None
    instrument_accrued_currency_fx_rate: float | None = None
    instrument_principal_price: float | None = None
    instrument_accrued_price: float | None = None
    instrument_factor: float | None = None
    instrument_ytm: float | None = None
    daily_price_change: float | None = None
    account: int | None = None
    strategy1: int | None = None
    strategy2: int | None = None
    strategy3: int | None = None
    fx_rate: float | None = None
    position_size: float | None = None
    period_start_position_size: float | None = None
    period_start_nominal_position_size: float | None = None
    mismatch: float | None = None
    nominal_position_size: float | None = None
    market_value: float | None = None
    market_value_loc: float | None = None
    exposure: float | None = None
    exposure_loc: float | None = None
    ytm: float | None = None
    ytm_at_cost: float | None = None
    modified_duration: float | None = None
    return_annually: float | None = None
    return_annually_fixed: float | None = None
    position_return: float | None = None
    position_return_loc: float | None = None
    net_position_return: float | None = None
    net_position_return_loc: float | None = None
    position_return_fixed: float | None = None
    position_return_fixed_loc: float | None = None
    net_position_return_fixed: float | None = None
    net_position_return_fixed_loc: float | None = None
    net_cost_price: float | None = None
    net_cost_price_loc: float | None = None
    gross_cost_price: float | None = None
    gross_cost_price_loc: float | None = None
    principal_invested: float | None = None
    principal_invested_loc: float | None = None
    amount_invested: float | None = None
    amount_invested_loc: float | None = None
    principal_invested_fixed: float | None = None
    principal_invested_fixed_loc: float | None = None
    amount_invested_fixed: float | None = None
    amount_invested_fixed_loc: float | None = None
    time_invested: float | None = None
    principal: float | None = None
    carry: float | None = None
    overheads: float | None = None
    total: float | None = None
    principal_fx: float | None = None
    carry_fx: float | None = None
    overheads_fx: float | None = None
    total_fx: float | None = None
    principal_fixed: float | None = None
    carry_fixed: float | None = None
    overheads_fixed: float | None = None
    total_fixed: float | None = None
    principal_loc: float | None = None
    carry_loc: float | None = None
    overheads_loc: float | None = None
    total_loc: float | None = None
    principal_fx_loc: float | None = None
    carry_fx_loc: float | None = None
    overheads_fx_loc: float | None = None
    total_fx_loc: float | None = None
    principal_fixed_loc: float | None = None
    carry_fixed_loc: float | None = None
    overheads_fixed_loc: float | None = None
    total_fixed_loc: float | None = None


@strawberry.type
class PLReport:
    items: list[PLReportItem]


@strawberry.field
def pl_report(
    self,
    info,
    input: PLReportInput,
    limit: int = 50,
    offset: int = 0,
) -> PLReport:
    user = info.context.request.user

    report_currency = CurrencyModel.objects.get(user_code=input.report_currency)
    pricing_policy = PricingPolicyModel.objects.get(user_code=input.pricing_policy)

    portfolios = []

    if input.portfolios:
        portfolios = PortfolioModel.objects.filter(user_code__in=input.portfolios)

    accounts = []

    if input.accounts:
        accounts = AccountModel.objects.filter(user_code__in=input.accounts)

    strategies1 = []

    if input.strategies1:
        strategies1 = Strategy1Model.objects.filter(user_code__in=input.strategies1)

    strategies2 = []

    if input.strategies2:
        strategies2 = Strategy2Model.objects.filter(user_code__in=input.strategies2)

    strategies3 = []

    if input.strategies3:
        strategies3 = Strategy3Model.objects.filter(user_code__in=input.strategies3)

    cost_method = CostMethodModel.objects.get(user_code="avco")

    if input.cost_method == "fifo":
        cost_method = CostMethodModel.objects.get(user_code="fifo")

    portfolio_mode = 1

    if input.portfolio_mode == "ignore":
        portfolio_mode = 0

    account_mode = 1

    if input.account_mode == "ignore":
        account_mode = 0

    strategy1_mode = 1

    if input.strategy1_mode == "ignore":
        strategy1_mode = 0

    strategy2_mode = 1

    if input.strategy2_mode == "ignore":
        strategy2_mode = 0

    strategy3_mode = 1

    if input.strategy3_mode == "ignore":
        strategy3_mode = 0

    report = ReportModel(
        master_user=user.master_user,
        member=user.member,
        calculate_pl=input.calculate_pl,
        cost_method=cost_method,
        custom_fields_to_calculate=input.custom_fields_to_calculate,
        calculation_group=input.calculation_group,
        report_date=input.report_date,
        pl_first_date=input.pl_first_date,
        period_type=input.period_type,
        pricing_policy=pricing_policy,
        report_currency=report_currency,
        portfolio_mode=portfolio_mode,
        account_mode=account_mode,
        strategy1_mode=strategy1_mode,
        strategy2_mode=strategy2_mode,
        strategy3_mode=strategy3_mode,
        portfolios=portfolios,
        accounts=accounts,
        strategies1=strategies1,
        strategies2=strategies2,
        strategies3=strategies3,
    )

    builder = PLReportBuilderSql(report)
    report = builder.build_pl_sync()

    items = []

    for item in report.items:
        items.append(serialize_pl_report_item(item))

    # _l.info('report.items %s' % items[0])

    # 3) map result to GraphQL types
    return PLReport(
        items=[PLReportItem(**row) for row in items],
    )


#  PERFORMANCE REPORT STARTS


@strawberry.input
class PerformanceReportInput:
    save_report: bool = False
    adjustment_type: str = "original"  # "original", "annualized"
    begin_date: date | None = None
    end_date: date
    calculation_type: str = "modified_dietz"
    segmentation_type: str = "months"  # "months", "days"
    period_type: str = "inception"  # "daily", "mtd", "ytd", "inception"
    report_currency: str = "USD"
    bundle: str | None = None  # user_code of bundle
    registers: list[str] = None  # list user_codes of portfolio registers


@strawberry.type
class PerformanceReport:
    begin_nav: float
    end_nav: float
    grand_absolute_pl: float
    grand_cash_flow: float
    grand_cash_flow_weighted: float
    grand_cash_inflow: float
    grand_cash_outflow: float
    grand_nav: float
    grand_return: float  # Main field for performance_report


@strawberry.field
def performance_report(
    self,
    info,
    input: PerformanceReportInput,
    limit: int = 50,
    offset: int = 0,
) -> PerformanceReport:
    user = info.context.request.user

    report_currency = CurrencyModel.objects.get(user_code=input.report_currency)
    registers = PortfolioRegisterModel.objects.filter(user_code__in=input.registers)

    try:
        bundle = PortfolioBundleModel.objects.get(user_code=input.bundle)
    except PortfolioBundleModel.DoesNotExist:
        bundle = None

    if not len(registers) and not bundle:
        raise Exception("registers or bundle are not provided")

    if bundle:
        instance = PerformanceReportModel(
            master_user=user.master_user,
            member=user.member,
            report_currency=report_currency,
            begin_date=input.begin_date,
            end_date=input.end_date,
            calculation_type=input.calculation_type,
            segmentation_type=input.segmentation_type,
            bundle=bundle,
        )
    elif len(registers):
        instance = PerformanceReportModel(
            master_user=user.master_user,
            member=user.member,
            report_currency=report_currency,
            begin_date=input.begin_date,
            end_date=input.end_date,
            calculation_type=input.calculation_type,
            segmentation_type=input.segmentation_type,
            registers=registers,
        )

    from poms.reports.performance_report import PerformanceReportBuilder

    builder = PerformanceReportBuilder(instance=instance)
    instance = builder.build_report()

    # _l.info('report.items %s' % items[0])

    # 3) map result to GraphQL types
    return PerformanceReport(
        begin_nav=instance.begin_nav,
        end_nav=instance.end_nav,
        grand_absolute_pl=instance.grand_absolute_pl,
        grand_cash_flow=instance.grand_cash_flow,
        grand_cash_flow_weighted=instance.grand_cash_flow_weighted,
        grand_cash_inflow=instance.grand_cash_inflow,
        grand_cash_outflow=instance.grand_cash_outflow,
        grand_nav=instance.grand_nav,
        grand_return=instance.grand_return,
    )


#  TRANSACTION REPORT STARTS


@strawberry.input
class TransactionReportInput:
    begin_date: date
    end_date: date
    depth_level: str = "entry"
    date_field: str = "transaction_date"

    expression_iterations_count: int = 1
    custom_fields_to_calculate: str = ""

    portfolios: list[str] | None = None
    accounts: list[str] | None = None
    strategies1: list[str] | None = None
    strategies2: list[str] | None = None
    strategies3: list[str] | None = None


@strawberry.type
class TransactionReportItem:
    id: str
    is_locked: bool | None = None
    is_canceled: bool | None = None
    notes: str | None = None
    transaction_code: int | None = None
    transaction_class: int | None = None
    complex_transaction: int | None = None
    portfolio: int | None = None
    counterparty: int | None = None
    responsible: int | None = None
    settlement_currency: int | None = None
    transaction_currency: int | None = None
    account_cash: int | None = None
    account_interim: int | None = None
    account_position: int | None = None
    allocation_balance: int | None = None
    allocation_pl: int | None = None
    instrument: int | None = None
    linked_instrument: int | None = None
    cash_consideration: float | None = None
    carry_amount: float | None = None
    carry_with_sign: float | None = None
    overheads_with_sign: float | None = None
    factor: float | None = None
    position_amount: float | None = None
    position_size_with_sign: float | None = None
    principal_amount: float | None = None
    principal_with_sign: float | None = None
    reference_fx_rate: float | None = None
    trade_price: float | None = None
    cash_date: date | None = None
    accounting_date: date | None = None
    transaction_date: date | None = None
    strategy1_cash: int | None = None
    strategy1_position: int | None = None
    strategy2_cash: int | None = None
    strategy2_position: int | None = None
    strategy3_cash: int | None = None
    strategy3_position: int | None = None
    transaction_item_name: str | None = None
    transaction_item_short_name: str | None = None
    transaction_item_user_code: str | None = None
    entry_account: str | None = None
    entry_strategy: str | None = None
    entry_item_short_name: str | None = None
    entry_item_user_code: str | None = None
    entry_item_name: str | None = None
    entry_item_public_name: str | None = None
    entry_currency: str | None = None
    entry_instrument: str | None = None
    entry_amount: float | None = None
    entry_item_type: float | None = None
    entry_item_type_name: float | None = None

    user_text_1: str | None = None
    user_text_2: str | None = None
    user_text_3: str | None = None

    user_number_1: str | None = None
    user_number_2: str | None = None
    user_number_3: str | None = None

    user_date_1: date | None = None
    user_date_2: date | None = None
    user_date_3: date | None = None


@strawberry.type
class TransactionReport:
    items: list[TransactionReportItem]


@strawberry.field
def transaction_report(
    self,
    info,
    input: TransactionReportInput,
    limit: int = 50,
    offset: int = 0,
) -> TransactionReport:
    user = info.context.request.user

    if input.portfolios:
        portfolios = PortfolioModel.objects.filter(user_code__in=input.portfolios)
    else:
        portfolios = []

    if input.accounts:
        accounts = AccountModel.objects.filter(user_code__in=input.accounts)
    else:
        accounts = []

    if input.strategies1:
        strategies1 = Strategy1Model.objects.filter(user_code__in=input.strategies1)
    else:
        strategies1 = []

    if input.strategies2:
        strategies2 = Strategy2Model.objects.filter(user_code__in=input.strategies2)
    else:
        strategies2 = []

    if input.strategies3:
        strategies3 = Strategy3Model.objects.filter(user_code__in=input.strategies3)
    else:
        strategies3 = []

    report = TransactionReportModel(
        master_user=user.master_user,
        member=user.member,
        custom_fields_to_calculate=input.custom_fields_to_calculate,
        begin_date=input.begin_date,
        end_date=input.end_date,
        date_field=input.date_field,
        depth_level=input.depth_level,
        portfolios=portfolios,
        accounts=accounts,
        strategies1=strategies1,
        strategies2=strategies2,
        strategies3=strategies3,
    )

    builder = TransactionReportBuilderSql(instance=report)
    instance = builder.build_transaction()

    items = []

    for item in instance.items:
        items.append(serialize_transaction_report_item(item))

    # _l.info('report.items %s' % items[0])

    # 3) map result to GraphQL types
    return TransactionReport(
        items=[from_dict(TransactionReportItem, row) for row in items],
    )


# PRICE HISTORY CHECK


@strawberry.input
class PriceHistoryCheckInput:
    pl_first_date: date | None = None
    report_date: date
    report_currency: str = "USD"
    period_type: str | None = None  # daily, mtd, qtd, ytd, inception

    pricing_policy: str | None = None
    calculate_pl: bool = False
    cost_method: str = "avco"  # avco or fifo
    expression_iterations_count: int = 1
    custom_fields_to_calculate: str = ""
    calculation_group: str = "portfolio.id"

    portfolios: list[str] | None = None
    accounts: list[str] | None = None
    strategies1: list[str] | None = None
    strategies2: list[str] | None = None
    strategies3: list[str] | None = None

    portfolio_mode: str = "independent"
    account_mode: str = "independent"
    strategy1_mode: str = "independent"
    strategy2_mode: str = "independent"
    strategy3_mode: str = "independent"


@strawberry.type
class PriceHistoryCheckItem:
    id: int | None = None
    name: str | None = None
    type: str  # missing_principal_pricing_history
    user_code: str | None = None
    position_size: float | None = None
    accounting_date: str | None = None
    transaction_currency_id: int | None = None
    transaction_currency_name: str | None = None
    transaction_currency_user_code: str | None = None
    settlement_currency_name: str | None = None
    settlement_currency_user_code: str | None = None


@strawberry.type
class PriceHistoryCheck:
    items: list[PriceHistoryCheckItem]


@strawberry.field
def price_history_check(
    self,
    info,
    input: PriceHistoryCheckInput,
    limit: int = 50,
    offset: int = 0,
) -> PriceHistoryCheck:
    user = info.context.request.user

    report_currency = CurrencyModel.objects.get(user_code=input.report_currency)
    pricing_policy = PricingPolicyModel.objects.get(user_code=input.pricing_policy)

    portfolios = []

    if input.portfolios:
        portfolios = PortfolioModel.objects.filter(user_code__in=input.portfolios)

    accounts = []

    if input.accounts:
        accounts = AccountModel.objects.filter(user_code__in=input.accounts)

    strategies1 = []

    if input.strategies1:
        strategies1 = Strategy1Model.objects.filter(user_code__in=input.strategies1)

    strategies2 = []

    if input.strategies2:
        strategies2 = Strategy2Model.objects.filter(user_code__in=input.strategies2)

    strategies3 = []

    if input.strategies3:
        strategies3 = Strategy3Model.objects.filter(user_code__in=input.strategies3)

    cost_method = CostMethodModel.objects.get(user_code="avco")

    if input.cost_method == "fifo":
        cost_method = CostMethodModel.objects.get(user_code="fifo")

    portfolio_mode = 1

    if input.portfolio_mode == "ignore":
        portfolio_mode = 0

    account_mode = 1

    if input.account_mode == "ignore":
        account_mode = 0

    strategy1_mode = 1

    if input.strategy1_mode == "ignore":
        strategy1_mode = 0

    strategy2_mode = 1

    if input.strategy2_mode == "ignore":
        strategy2_mode = 0

    strategy3_mode = 1

    if input.strategy3_mode == "ignore":
        strategy3_mode = 0

    report = ReportModel(
        master_user=user.master_user,
        member=user.member,
        calculate_pl=input.calculate_pl,
        cost_method=cost_method,
        custom_fields_to_calculate=input.custom_fields_to_calculate,
        calculation_group=input.calculation_group,
        report_date=input.report_date,
        pl_first_date=input.pl_first_date,
        period_type=input.period_type,
        pricing_policy=pricing_policy,
        report_currency=report_currency,
        portfolio_mode=portfolio_mode,
        account_mode=account_mode,
        strategy1_mode=strategy1_mode,
        strategy2_mode=strategy2_mode,
        strategy3_mode=strategy3_mode,
        portfolios=portfolios,
        accounts=accounts,
        strategies1=strategies1,
        strategies2=strategies2,
        strategies3=strategies3,
    )

    builder = PriceHistoryCheckerSql(instance=report)
    instance = builder.process()

    items = []

    for item in instance.items:
        items.append(serialize_price_checker_item(item))

    # _l.info('report.items %s' % items[0])

    # 3) map result to GraphQL types
    return PriceHistoryCheck(
        items=[from_dict(PriceHistoryCheckItem, row) for row in items],
    )


@strawberry.type
class Query:
    account: list[Account] = strawberry_django.field(
        filters=AccountFilter,
        order=AccountOrdering,
        pagination=True,
    )
    account_type: list[AccountType] = strawberry_django.field(
        filters=AccountTypeFilter,
        order=AccountTypeOrdering,
        pagination=True,
    )

    currency: list[Currency] = strawberry_django.field(
        filters=CurrencyFilter,
        order=CurrencyOrdering,
        pagination=True,
    )

    currency_history: list[CurrencyHistory] = strawberry_django.field(
        filters=CurrencyHistoryFilter,
        order=CurrencyHistoryOrdering,
        pagination=True,
    )

    portfolio: list[Portfolio] = strawberry_django.field(
        filters=PortfolioFilter,
        order=PortfolioOrdering,
        pagination=True,
    )

    portfolio_history: list[PortfolioHistory] = strawberry_django.field(
        filters=PortfolioHistoryFilter,
        order=PortfolioHistoryOrdering,
        pagination=True,
    )

    instrument_type: list[InstrumentType] = strawberry_django.field(
        filters=InstrumentTypeFilter,
        order=InstrumentTypeOrdering,
        pagination=True,
    )

    instrument: list[Instrument] = strawberry_django.field(
        filters=InstrumentFilter,
        order=InstrumentOrdering,
        pagination=True,
    )

    pricing_policy: list[PricingPolicy] = strawberry_django.field(
        filters=PricingPolicyFilter,
        order=PricingPolicyOrdering,
        pagination=True,
    )

    price_history: list[PriceHistory] = strawberry_django.field(
        filters=PriceHistoryFilter,
        order=PriceHistoryOrdering,
        pagination=True,
    )

    responsible: list[Responsible] = strawberry_django.field(
        filters=ResponsibleFilter,
        order=ResponsibleOrdering,
        pagination=True,
    )

    counterparty: list[Counterparty] = strawberry_django.field(
        filters=CounterpartyFilter,
        order=CounterpartyOrdering,
        pagination=True,
    )

    strategy1: list[Strategy1] = strawberry_django.field(
        filters=Strategy1Filter,
        order=Strategy1Ordering,
        pagination=True,
    )

    strategy2: list[Strategy2] = strawberry_django.field(
        filters=Strategy2Filter,
        order=Strategy2Ordering,
        pagination=True,
    )

    strategy3: list[Strategy3] = strawberry_django.field(
        filters=Strategy3Filter,
        order=Strategy3Ordering,
        pagination=True,
    )

    complex_transaction: list[ComplexTransaction] = strawberry_django.field(
        filters=ComplexTransactionFilter,
        order=ComplexTransactionOrdering,
        pagination=True,
    )

    transaction: list[Transaction] = strawberry_django.field(
        filters=TransactionFilter,
        order=TransactionOrdering,
        pagination=True,
    )

    balance_report: BalanceReport = balance_report
    pl_report: PLReport = pl_report
    performance_report: PerformanceReport = performance_report
    transaction_report: TransactionReport = transaction_report
    price_history_check: PriceHistoryCheck = price_history_check


schema = strawberry.Schema(
    query=Query,
    config=StrawberryConfig(auto_camel_case=False),  # keep snake_case
)
