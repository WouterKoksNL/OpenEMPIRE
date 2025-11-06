
from empire.core.config import EmpireConfiguration

from .base.expressions import define_base_investment_expressions
from .heat.expressions import define_heat_investment_expressions
from .hydrogen.expressions import define_hydrogen_investment_expressions
from .industry.expressions import define_industry_investment_expressions

def define_investment_expressions(model, empire_config: EmpireConfiguration, periods_active, flags):
    define_base_investment_expressions(model)
    if flags.heat:
        define_heat_investment_expressions(model)
    if flags.hydrogen:
        define_hydrogen_investment_expressions(model, empire_config.gas_h2_repurpose_cost_factor)
    if flags.industry:
        define_industry_investment_expressions(model, empire_config.steel_CCS_cost_increase)