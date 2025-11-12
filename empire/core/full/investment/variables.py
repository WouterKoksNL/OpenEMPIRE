
from .base.variables import define_base_investment_variables
from .heat.variables import define_heat_investment_variables
from .industry.variables import define_industry_investment_variables
from .hydrogen.variables import define_hydrogen_investment_variables
from .offshore_converters.variables import define_offshore_converter_investment_variables

def define_investment_variables(model, empire_config):
    define_base_investment_variables(model)

    if empire_config.offshore_converters_flag:
        define_offshore_converter_investment_variables(model)

    if empire_config.heat_flag:
        define_heat_investment_variables(model)

    if empire_config.industry_flag:
        define_industry_investment_variables(model)

    if empire_config.hydrogen_flag:
        define_hydrogen_investment_variables(model)