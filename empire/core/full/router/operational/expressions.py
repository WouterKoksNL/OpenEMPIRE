from empire_types import Flags
from base.operational.expressions import define_base_operational_build_actions, define_base_operational_expressions
from natural_gas.expressions import define_natural_gas_expressions
from heat.operational.expressions import define_heat_operational_expressions
from hydrogen.operational.expressions import define_hydrogen_operational_expressions
from industry.operational.expressions import define_industry_operational_expressions


def define_operational_expressions(model, lengthRegSeason, NoOfRegSeason, lengthPeakSeason, NoOfPeakSeason, LeapYearsInvestment, result_file_path, EMISSION_CAP, steel_CCS_capture_rate, flags):
    """Define operational expressions in the correct dependency order.
    
    Order is critical:
    1. Base build actions (create foundational parameters like seasScale, sceProbab, operationalDiscountrate)
       - Called from here since shared expressions depend on them
    2. Heat expressions (modify genVariableOMCost and other params used by base expressions)
    3. Base operational expressions (use the modified parameters to create genMargCost, etc.)
    4. Other module expressions (depend on base expressions)
    
    Note: Shared expressions (hydrogen, heat) are called from empire.py after this,
    but they depend on the build actions created here.
    """
    
    # Step 1: Base build actions that create foundational parameters
    # These MUST be first as shared expressions and heat expressions depend on them
    define_base_operational_build_actions(model, lengthRegSeason, NoOfRegSeason, lengthPeakSeason, NoOfPeakSeason, LeapYearsInvestment, result_file_path, flags)
    
    # Step 2: Heat expressions that modify parameters used in base expressions
    if flags.heat:
        define_heat_operational_expressions(model, result_file_path)
    

    # Step 4: Other module expressions
    if flags.natural_gas:
        define_natural_gas_expressions(model)
    if flags.hydrogen:
        define_hydrogen_operational_expressions(model)
    if flags.industry:
        define_industry_operational_expressions(model, EMISSION_CAP, steel_CCS_capture_rate)

    # Step 3: Base operational expressions that use modified parameters
    define_base_operational_expressions(model, EMISSION_CAP, flags)
    