
from .base.variables import define_base_operational_variables
from .natural_gas.variables import define_natural_gas_operational_variables
from .heat.variables import define_heat_operational_variables
from .industry.variables import define_industry_operational_variables
from .hydrogen.variables import define_hydrogen_operational_variables


def define_operational_variables(model, flags):
    define_base_operational_variables(model, flags.cvar)

    if flags.natural_gas:
        define_natural_gas_operational_variables(model)

    if flags.heat:
        define_heat_operational_variables(model)

    if flags.industry:
        define_industry_operational_variables(model)

    if flags.hydrogen:
        define_hydrogen_operational_variables(model)