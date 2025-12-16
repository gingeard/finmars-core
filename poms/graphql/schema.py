from __future__ import annotations

import logging
from datetime import date

import strawberry
import strawberry_django
from strawberry.schema.config import StrawberryConfig
from dataclasses import field

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
    PriceHistoryFilter,
    ResponsibleFilter,
    Strategy1Filter,
    Strategy2Filter,
    Strategy3Filter,
    TransactionFilter, PricingPolicyFilter, PortfolioHistoryFilter,
)
from poms.instruments.models import Country as CountryModel
from poms.instruments.models import Instrument as InstrumentModel
from poms.instruments.models import InstrumentType as InstrumentTypeModel
from poms.instruments.models import PriceHistory as PriceHistoryModel
from poms.instruments.models import PricingPolicy as PricingPolicyModel
from poms.instruments.models import CostMethod as CostMethodModel
from poms.portfolios.models import Portfolio as PortfolioModel
from poms.portfolios.models import PortfolioHistory as PortfolioHistoryModel
from poms.portfolios.models import PortfolioRegister as PortfolioRegisterModel
from poms.portfolios.models import PortfolioBundle as PortfolioBundleModel
from poms.reports.common import Report
from poms.reports.serializers_helpers import serialize_balance_report_item
from poms.reports.sql_builders.balance import BalanceReportBuilderSql
from poms.reports.common import PerformanceReport as PerformanceReportModel
from poms.strategies.models import Strategy1 as Strategy1Model
from poms.strategies.models import Strategy2 as Strategy2Model
from poms.strategies.models import Strategy3 as Strategy3Model
from poms.transactions.models import ComplexTransaction as ComplexTransactionModel
from poms.transactions.models import Transaction as TransactionModel
from poms.transactions.models import TransactionClass as TransactionClassModel
from poms.users.models import Member as MemberModel

_l = logging.getLogger("poms.graphql")

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
    cost_method: str = "avco" # avco or fifo
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

    cost_method = CostMethodModel.objects.get(user_code="avco")

    if input.cost_method == "fifo":
        cost_method = CostMethodModel.objects.get(user_code="fifo")

    portfolio_mode = 1

    if input.portfolio_mode == 'ignore':
        portfolio_mode = 0


    account_mode = 1

    if input.account_mode == 'ignore':
        account_mode = 0

    strategy1_mode = 1

    if input.strategy1_mode == 'ignore':
        strategy1_mode = 0

    strategy2_mode = 1

    if input.strategy2_mode == 'ignore':
        strategy2_mode = 0


    strategy3_mode = 1

    if input.strategy3_mode == 'ignore':
        strategy3_mode = 0

    report = Report(
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
    pl_first_date: date
    report_date: date
    report_currency: str | None = None
    portfolios: list[str] | None = None
    pricing_policy: str | None = None


@strawberry.type
class PLReportItem:
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
    portfolios = PortfolioModel.objects.filter(user_code__in=input.portfolios)

    report = Report(
        master_user=user.master_user,
        member=user.member,
        pl_first_date=input.pl_first_date,
        report_date=input.report_date,
        pricing_policy=pricing_policy,
        portfolios=portfolios,
        report_currency=report_currency,
    )

    builder = BalanceReportBuilderSql(report)
    report = builder.build_balance_sync()

    items = []

    for item in report.items:
        items.append(serialize_balance_report_item(item)) # TODO change to PL report serializer

    # _l.info('report.items %s' % items[0])

    # 3) map result to GraphQL types
    return PLReport(
        items=[PLReportItem(**row) for row in items],
    )


#  PERFORMANCE REPORT STARTS



@strawberry.input
class PerformanceReportInput:
    save_report: bool = False
    adjustment_type: str = "original" # "original", "annualized"
    begin_date: date | None = None
    end_date: date
    calculation_type: str = "modified_dietz"
    segmentation_type: str = "months" # "months", "days"
    period_type: str = "inception" # "daily", "mtd", "ytd", "inception"
    report_currency: str = "USD"
    bundle: str | None = None # user_code of bundle
    registers: list[str] = None # list user_codes of portfolio registers


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
    grand_return: float # Main field for performance_report


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

    _l.info('registers %s' % registers)

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



@strawberry.type
class Query:
    account: list[Account] = strawberry_django.field(
        filters=AccountFilter,
        pagination=True,
    )
    account_type: list[AccountType] = strawberry_django.field(
        filters=AccountTypeFilter,
        pagination=True,
    )

    currency: list[Currency] = strawberry_django.field(
        filters=CurrencyFilter,
        pagination=True,
    )

    currency_history: list[CurrencyHistory] = strawberry_django.field(
        filters=CurrencyHistoryFilter,
        pagination=True,
    )

    portfolio: list[Portfolio] = strawberry_django.field(
        filters=PortfolioFilter,
        pagination=True,
    )

    portfolio_history: list[PortfolioHistory] = strawberry_django.field(
        filters=PortfolioHistoryFilter,
        pagination=True,
    )

    instrument_type: list[InstrumentType] = strawberry_django.field(
        filters=InstrumentTypeFilter,
        pagination=True,
    )

    instrument: list[Instrument] = strawberry_django.field(
        filters=InstrumentFilter,
        pagination=True,
    )

    pricing_policy: list[PricingPolicy] = strawberry_django.field(
        filters=PricingPolicyFilter,
        pagination=True,
    )

    price_history: list[PriceHistory] = strawberry_django.field(
        filters=PriceHistoryFilter,
        pagination=True,
    )

    responsible: list[Responsible] = strawberry_django.field(
        filters=ResponsibleFilter,
        pagination=True,
    )

    counterparty: list[Counterparty] = strawberry_django.field(
        filters=CounterpartyFilter,
        pagination=True,
    )

    strategy1: list[Strategy1] = strawberry_django.field(
        filters=Strategy1Filter,
        pagination=True,
    )

    strategy2: list[Strategy1] = strawberry_django.field(
        filters=Strategy2Filter,
        pagination=True,
    )

    strategy3: list[Strategy1] = strawberry_django.field(
        filters=Strategy3Filter,
        pagination=True,
    )

    complex_transaction: list[ComplexTransaction] = strawberry_django.field(
        filters=ComplexTransactionFilter,
        pagination=True,
    )

    transaction: list[Transaction] = strawberry_django.field(
        filters=TransactionFilter,
        pagination=True,
    )

    balance_report: BalanceReport = balance_report
    pl_report: PLReport = pl_report
    performance_report: PerformanceReport = performance_report


schema = strawberry.Schema(
    query=Query,
    config=StrawberryConfig(auto_camel_case=False),  # keep snake_case
)
