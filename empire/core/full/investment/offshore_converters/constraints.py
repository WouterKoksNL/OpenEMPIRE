from pyomo.core import Constraint, value

def define_offshore_converter_investment_constraints(model):
    # GD: Linking offshoreConvInvCap and offshoreConvInstalledCap variables
    def lifetime_rule_conver(model,n, i):
        startPeriod=1
        if value(1+i-model.offshoreConvLifetime*(1/model.leap_years_investment))>startPeriod:
            startPeriod=value(1+i-model.offshoreConvLifetime*(1/model.leap_years_investment))
        return sum(model.offshoreConvInvCap[n,j] for j in model.Period if j>=startPeriod and j<=i) - model.offshoreConvInstalledCap[n,i] == 0
    model.installedCapDefinitionConv = Constraint(model.OffshoreEnergyHubs, model.Period, rule=lifetime_rule_conver)