
from empire.core.config import EmpireConfiguration

from .base.expressions import define_base_investment_expressions
from .heat.expressions import define_heat_investment_expressions
from .hydrogen.expressions import define_hydrogen_investment_expressions
from .industry.expressions import define_industry_investment_expressions
from .offshore_converters.expressions import define_offshore_converter_investment_expressions

def define_investment_expressions(model, empire_config: EmpireConfiguration):
    define_base_investment_expressions(model)

    if empire_config.offshore_converters_flag:
        define_offshore_converter_investment_expressions(model)
    if empire_config.heat_flag:
        define_heat_investment_expressions(model)
    if empire_config.hydrogen_flag:
        define_hydrogen_investment_expressions(model, empire_config.gas_h2_repurpose_cost_factor)
    if empire_config.industry_flag:
        define_industry_investment_expressions(model, empire_config.steel_CCS_cost_increase)