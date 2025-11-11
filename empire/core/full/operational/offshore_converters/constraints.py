from pyomo.environ import Constraint

def define_operational_offshore_converter_constraints(model):
        
        # GD: Ensuring that power sent from offshore hub is no greater than its capacity
        def offshore_hub_capacity_in_rule(model, n,h,i,w,gp):
            return sum(model.transmissionOperational[n2,n,h,i,w,gp] for n2 in model.NodesLinked[n]) - model.offshoreConvInstalledCap[n,i] <= 0
        model.offshore_hub_capacity_in = Constraint(model.OffshoreEnergyHubs, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=offshore_hub_capacity_in_rule)

        def offshore_hub_capacity_out_rule(model, n,h,i,w,gp):
            return sum(model.transmissionOperational[n,n2,h,i,w,gp] for n2 in model.NodesLinked[n]) - model.offshoreConvInstalledCap[n,i] <= 0
        model.offshore_hub_capacity_out = Constraint(model.OffshoreEnergyHubs, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, rule=offshore_hub_capacity_out_rule)
