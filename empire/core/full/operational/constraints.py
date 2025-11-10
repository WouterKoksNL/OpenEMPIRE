from empire.core.config import EmpireConfiguration

from .base.constraints import define_base_operational_constraints
from .natural_gas.constraints import define_operational_natural_gas_constraints
from .heat.constraints import define_operational_heat_constraints
from .hydrogen.constraints import define_operational_hydrogen_constraints
from .industry.constraints import define_industry_operational_constraints
from .offshore_converters.constraints import define_operational_offshore_converter_constraints

def define_operational_constraints(model, empire_config: EmpireConfiguration, flags):
    define_base_operational_constraints(model, empire_config.emission_cap_flag, flags)
    
    if flags.offshore_converters:
        define_operational_offshore_converter_constraints(model)

    if flags.natural_gas:
        define_operational_natural_gas_constraints(model, empire_config.leap_years_investment, flags.hydrogen, flags.industry)

    if flags.heat:
        define_operational_heat_constraints(model)

    if flags.hydrogen:
        define_operational_hydrogen_constraints(model, flags.industry, empire_config.leap_years_investment)

    if flags.industry:
        define_industry_operational_constraints(model, empire_config.industry_flexibility_flag)

    

