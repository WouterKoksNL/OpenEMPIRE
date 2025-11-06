
from .base.variables import define_base_investment_variables
from .heat.variables import define_heat_investment_variables
from .industry.variables import define_industry_investment_variables
from .hydrogen.variables import define_hydrogen_investment_variables


def define_investment_variables(model, flags):
    define_base_investment_variables(model)

    if flags.heat:
        define_heat_investment_variables(model)

    if flags.industry:
        define_industry_investment_variables(model)

    if flags.hydrogen:
        define_hydrogen_investment_variables(model)