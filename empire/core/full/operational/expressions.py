from pyomo.environ import ConcreteModel

from empire.core.config import EmpireConfiguration
from .base.expressions import define_base_operational_build_actions, define_base_operational_expressions, derive_instance_base_stochastic_parameters
from .natural_gas.expressions import define_natural_gas_expressions
from .heat.expressions import define_heat_operational_expressions
from .hydrogen.expressions import define_hydrogen_operational_expressions
from .industry.expressions import define_industry_operational_expressions


def define_operational_expressions(model, empire_config: EmpireConfiguration, result_file_path, logger):
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
    define_base_operational_build_actions(model, empire_config)
    
    # Step 2: Heat expressions that modify parameters used in base expressions
    if empire_config.heat_flag:
        define_heat_operational_expressions(model, result_file_path)
    

    # Step 4: Other module expressions
    if empire_config.natural_gas_flag:
        define_natural_gas_expressions(model)
    if empire_config.hydrogen_flag:
        define_hydrogen_operational_expressions(model)
    if empire_config.industry_flag:
        define_industry_operational_expressions(model, empire_config.emission_cap_flag, empire_config.steel_CCS_capture_rate)

    # Step 3: Base operational expressions that use modified parameters
    define_base_operational_expressions(model, empire_config, logger)


def derive_instance_stochastic_parameters(instance: ConcreteModel, empire_config: EmpireConfiguration, node_unscaled_yearly_demand_ser=None) -> None:
    """Set values for stochastic parameters based on raw inputs.
    E.g. compute sload from sloadRaw."""
    
    derive_instance_base_stochastic_parameters(instance, empire_config, node_unscaled_yearly_demand_ser)
    
