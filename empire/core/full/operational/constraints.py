from empire.core.config import EmpireConfiguration

from .base.constraints import define_base_operational_constraints
from .natural_gas.constraints import define_operational_natural_gas_constraints
from .heat.constraints import define_operational_heat_constraints
from .hydrogen.constraints import define_operational_hydrogen_constraints
from .industry.constraints import define_industry_operational_constraints
from .offshore_converters.constraints import define_operational_offshore_converter_constraints

def define_operational_constraints(model, empire_config: EmpireConfiguration):
    define_base_operational_constraints(model, empire_config)

    if empire_config.offshore_converters_flag:
        define_operational_offshore_converter_constraints(model)

    if empire_config.natural_gas_flag:
        define_operational_natural_gas_constraints(model, empire_config.leap_years_investment, empire_config.hydrogen_flag, empire_config.industry_flag)

    if empire_config.heat_flag:
        define_operational_heat_constraints(model)

    if empire_config.hydrogen_flag:
        define_operational_hydrogen_constraints(model, empire_config.industry_flag, empire_config.leap_years_investment)

    if empire_config.industry_flag:
        define_industry_operational_constraints(model, empire_config.industry_flexibility_flag)

    

