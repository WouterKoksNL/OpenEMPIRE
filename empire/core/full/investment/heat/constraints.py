"""Heat module investment constraints."""
from pyomo.environ import Constraint, value


def define_heat_investment_constraints(model):
    """Define constraints for heat module converter investment.
    """
    
    def lifetime_rule_Converter(model, n, r, i):
        """Link converter investments over time to installed capacity."""
        startPeriod = 1
        if value(1 + i - (model.ConverterLifetime[r] / model.leap_years_investment)) > startPeriod:
            startPeriod = value(1 + i - model.ConverterLifetime[r] / model.leap_years_investment)
        return sum(model.ConverterInvCap[n, r, j] for j in model.Period if j >= startPeriod and j <= i) - \
               model.ConverterInstalledCap[n, r, i] + model.ConverterInitCap[n, r, i] == 0
    model.installedCapDefinitionConverter = Constraint(model.ConverterOfNode, model.Period, 
                                                       rule=lifetime_rule_Converter)
    
    def investment_Converter_cap_rule(model, n, r, i):
        """Limit converter investment capacity."""
        return model.ConverterInvCap[n, r, i] - model.ConverterMaxBuiltCap[n, r, i] <= 0
    model.investment_Converter_cap = Constraint(model.ConverterOfNode, model.Period, 
                                                rule=investment_Converter_cap_rule)


