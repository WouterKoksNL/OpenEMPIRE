from empire_types import Flags
from base.investment.variables import define_base_investment_variables
from heat.investment.variables import define_heat_investment_variables
from industry.investment.variables import define_industry_investment_variables
from hydrogen.investment.variables import define_hydrogen_investment_variables


def define_investment_variables(model, flags: Flags):
    define_base_investment_variables(model)

    if flags.heat:
        define_heat_investment_variables(model)

    if flags.industry:
        define_industry_investment_variables(model)

    if flags.hydrogen:
        define_hydrogen_investment_variables(model)