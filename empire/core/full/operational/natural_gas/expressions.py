from pyomo.environ import Expression


def define_natural_gas_expressions(model):
    
    def ng_import_cost_rule(model,i,w, gp):
        return sum(model.operationalDiscountrate * model.seasScale[s] * model.ng_terminalImport[n,t,h,i,w,gp] * model.ng_terminalCost[n,t,i,gp] for (n,t) in model.NaturalGasTerminalsOfNode for (s,h) in model.HoursOfSeason)
    model.ng_import_cost = Expression(model.Period, model.Scenario, model.GasScenario, rule=ng_import_cost_rule)