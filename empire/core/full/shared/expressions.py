from empire.core.config import EmpireConfiguration


def define_shared_expressions(model, empire_config: EmpireConfiguration):
    """Define shared expressions that depend on base operational build actions.
    
    These expressions use parameters created by base operational build actions
    (like operationalDiscountrate, seasScale) so must be called after those.
    """
    if empire_config.hydrogen_flag:
        from .hydrogen.expressions import define_hydrogen_shared_expressions
        define_hydrogen_shared_expressions(model)
    
    if empire_config.heat_flag:
        from .heat.expressions import define_heat_shared_expressions
        define_heat_shared_expressions(model)
