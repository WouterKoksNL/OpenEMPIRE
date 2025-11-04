

def define_shared_expressions(model, flags):
    """Define shared expressions that depend on base operational build actions.
    
    These expressions use parameters created by base operational build actions
    (like operationalDiscountrate, seasScale) so must be called after those.
    """
    if flags.hydrogen:
        from hydrogen.shared.expressions import define_hydrogen_shared_expressions
        define_hydrogen_shared_expressions(model)
    
    if flags.heat:
        from heat.shared.expressions import define_heat_shared_expressions
        define_heat_shared_expressions(model)
