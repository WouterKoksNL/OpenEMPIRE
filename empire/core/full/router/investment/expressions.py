from empire_types import Flags

from base.investment.expressions import define_base_investment_expressions
from heat.investment.expressions import define_heat_investment_expressions
from hydrogen.investment.expressions import define_hydrogen_investment_expressions
from industry.investment.expressions import define_industry_investment_expressions

def define_investment_expressions(model, LeapYearsInvestment, Period, repurposeCostFactor, steel_CCS_cost_increase, flags: Flags):
    define_base_investment_expressions(model, LeapYearsInvestment)
    if flags.heat:
        define_heat_investment_expressions(model, Period, LeapYearsInvestment)
    if flags.hydrogen:
        define_hydrogen_investment_expressions(model, LeapYearsInvestment, repurposeCostFactor)
    if flags.industry:
        define_industry_investment_expressions(model, LeapYearsInvestment, steel_CCS_cost_increase)