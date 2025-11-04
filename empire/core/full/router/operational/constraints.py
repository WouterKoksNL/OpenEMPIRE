from empire_types import Flags

from base.operational.constraints import define_base_operational_constraints
from natural_gas.constraints import define_operational_natural_gas_constraints
from heat.operational.constraints import define_operational_heat_constraints
from hydrogen.operational.constraints import define_operational_hydrogen_constraints
from industry.operational.constraints import define_industry_operational_constraints

def define_operational_constraints(model, EMISSION_CAP, FLEX_IND: bool, LeapYearsInvestment, flags: Flags):
    define_base_operational_constraints(model, EMISSION_CAP, flags)
    
    if flags.natural_gas:
        define_operational_natural_gas_constraints(model, LeapYearsInvestment, flags.hydrogen, flags.industry)
        
    if flags.heat:
        define_operational_heat_constraints(model)

    if flags.hydrogen:
        define_operational_hydrogen_constraints(model, flags.industry, LeapYearsInvestment)

    if flags.industry:
        define_industry_operational_constraints(model, FLEX_IND)

    

