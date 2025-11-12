from empire.core.config import EmpireConfiguration
from .base.variables import define_base_operational_variables
from .natural_gas.variables import define_natural_gas_operational_variables
from .heat.variables import define_heat_operational_variables
from .industry.variables import define_industry_operational_variables
from .hydrogen.variables import define_hydrogen_operational_variables


def define_operational_variables(model, empire_config: EmpireConfiguration):
    define_base_operational_variables(model, empire_config.cvar_flag)

    if empire_config.natural_gas_flag:
        define_natural_gas_operational_variables(model)

    if empire_config.heat_flag:
        define_heat_operational_variables(model)

    if empire_config.industry_flag:
        define_industry_operational_variables(model)

    if empire_config.hydrogen_flag:
        define_hydrogen_operational_variables(model)