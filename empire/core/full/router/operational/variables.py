from empire_types import Flags
from base.operational.variables import define_base_operational_variables
from natural_gas.variables import define_natural_gas_operational_variables
from heat.operational.variables import define_heat_operational_variables
from industry.operational.variables import define_industry_operational_variables
from hydrogen.operational.variables import define_hydrogen_operational_variables


def define_operational_variables(model, flags: Flags):
    # Operational variables
    define_base_operational_variables(model, flags.cvar)

    # Natural gas operational variables
    define_natural_gas_operational_variables(model)
    if flags.heat:
        define_heat_operational_variables(model)

    if flags.industry:
        define_industry_operational_variables(model)

    if flags.hydrogen:
        define_hydrogen_operational_variables(model)