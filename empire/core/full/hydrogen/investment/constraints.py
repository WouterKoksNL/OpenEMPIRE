"""Hydrogen investment constraints."""
from pyomo.environ import Constraint, value

from constants import Constants

def define_hydrogen_investment_constraints(model, LeapYearsInvestment, 
                                           repurposeEnergyFlowFactor=1.0, 
    ):
    """Define constraints for hydrogen infrastructure investment.
    
    Args:
        model: Pyomo abstract model
        LeapYearsInvestment: Number of years per investment period
        repurposeEnergyFlowFactor: Repurpose energy flow factor
    """
    
    # Repurposed pipeline capacity constraint
    def repurpose_cap_rule(model, n1, n2, i):
        """Limit repurposed pipeline capacity to existing natural gas capacity."""
        return model.repurposedPipelineBuilt[n1, n2, i] - model.ng_pipelineCapacity[n1, n2] <= 0
    model.repurpose_cap = Constraint(model.RepurposeDirectionalLinks, model.Period, rule=repurpose_cap_rule)
    
    # Hydrogen pipeline lifetime constraint
    ng_h2_conversion_factor = Constants.ng_MWhPerTon / Constants.hydrogen_MWhPerTon
    def lifetime_rule_pipeline(model, n1, n2, i):
        """Link hydrogen pipeline investments over time to installed capacity."""
        startPeriod = 1
        if value(1 + i - model.hydrogenPipelineLifetime / LeapYearsInvestment) > startPeriod:
            startPeriod = value(1 + i - model.hydrogenPipelineLifetime / LeapYearsInvestment)
        
        # Handle different repurposing scenarios
        if (n1, n2) in model.RepurposeDirectionalLinks and (n2, n1) in model.RepurposeDirectionalLinks:
            return sum((model.hydrogenPipelineBuilt[n1, n2, j] + 
                       model.repurposedPipelineBuilt[n1, n2, j] * ng_h2_conversion_factor * repurposeEnergyFlowFactor +
                       model.repurposedPipelineBuilt[n2, n1, j] * ng_h2_conversion_factor * repurposeEnergyFlowFactor) 
                      for j in model.Period if j >= startPeriod and j <= i) - \
                   model.totalHydrogenPipelineCapacity[n1, n2, i] == 0
        elif (n1, n2) in model.RepurposeDirectionalLinks:
            return sum((model.hydrogenPipelineBuilt[n1, n2, j] + 
                       model.repurposedPipelineBuilt[n1, n2, j] * ng_h2_conversion_factor * repurposeEnergyFlowFactor) 
                      for j in model.Period if j >= startPeriod and j <= i) - \
                   model.totalHydrogenPipelineCapacity[n1, n2, i] == 0
        elif (n2, n1) in model.RepurposeDirectionalLinks:
            return sum((model.hydrogenPipelineBuilt[n1, n2, j] + 
                       model.repurposedPipelineBuilt[n2, n1, j] * ng_h2_conversion_factor * repurposeEnergyFlowFactor) 
                      for j in model.Period if j >= startPeriod and j <= i) - \
                   model.totalHydrogenPipelineCapacity[n1, n2, i] == 0
        else:
            return sum(model.hydrogenPipelineBuilt[n1, n2, j] for j in model.Period if j >= startPeriod and j <= i) - \
                   model.totalHydrogenPipelineCapacity[n1, n2, i] == 0
    model.installedCapDefinitionPipe = Constraint(model.HydrogenBidirectionPipelines, model.Period, 
                                                  rule=lifetime_rule_pipeline)
    
    # Electrolyzer lifetime constraint
    def lifetime_rule_elyzer(model, n, i):
        """Link electrolyzer investments over time to installed capacity."""
        startPeriod = 1
        if value(1 + i - model.elyzerLifetime / LeapYearsInvestment) > startPeriod:
            startPeriod = value(1 + i - model.elyzerLifetime / LeapYearsInvestment)
        return sum(model.elyzerCapBuilt[n, j] for j in model.Period if j >= startPeriod and j <= i) - \
               model.elyzerTotalCap[n, i] == 0
    model.installedCapDefinitionElyzer = Constraint(model.HydrogenProdNode, model.Period, rule=lifetime_rule_elyzer)
    
    # Reformer lifetime constraint
    def lifetime_rule_reformer(model, n, p, i):
        """Link reformer investments over time to installed capacity."""
        startPeriod = 1
        if value(1 + i - model.ReformerPlantLifetime[p] / LeapYearsInvestment) > startPeriod:
            startPeriod = value(1 + i - model.ReformerPlantLifetime[p] / LeapYearsInvestment)
        return sum(model.ReformerCapBuilt[n, p, j] for j in model.Period if j >= startPeriod and j <= i) - \
               model.ReformerTotalCap[n, p, i] == 0
    model.installedCapDefinitionReformer = Constraint(model.ReformerLocations, model.ReformerPlants, model.Period, 
                                                      rule=lifetime_rule_reformer)
    
    # Hydrogen storage constraints
    def hydrogen_storage_max_capacity_rule(model, n, b, i):
        """Limit total hydrogen storage capacity."""
        return model.hydrogenTotalStorage[n, b, i] / 1e3 <= model.hydrogenMaxStorageCapacity[n, b] / 1e3
    model.hydrogen_storage_max_capacity = Constraint(model.HydrogenProdNode, model.H2Storages, model.Period,
                                                     rule=hydrogen_storage_max_capacity_rule)
    
    def hydrogen_storage_lifetime_rule(model, n, b, i):
        """Link hydrogen storage investments over time to installed capacity."""
        startPeriod = 1
        if value(1 + i - model.hydrogenStorageLifetime[b] / LeapYearsInvestment) > startPeriod:
            startPeriod = value(1 + i - model.hydrogenStorageLifetime[b] / LeapYearsInvestment)
        return sum(model.hydrogenStorageBuilt[n, b, j] for j in model.Period if j >= startPeriod and j <= i) - \
               model.hydrogenTotalStorage[n, b, i] == 0
    model.hydrogen_storage_lifetime = Constraint(model.HydrogenProdNode, model.H2Storages, model.Period,
                                                rule=hydrogen_storage_lifetime_rule)
    
    # H2 import terminal lifetime constraint
    def lifetime_rule_H2import(model, n, t, i):
        """Link H2 import terminal investments over time to installed capacity."""
        startPeriod = 1
        if value(1 + i - model.H2TerminalLifetime[t] / LeapYearsInvestment) > startPeriod:
            startPeriod = value(1 + i - model.H2TerminalLifetime[t] / LeapYearsInvestment)
        return sum(model.H2ImportCapBuilt[n, t, j] for j in model.Period if j >= startPeriod and j <= i) - \
               model.H2ImportTotalCap[n, t, i] == 0
    model.installedCapDefinitionH2Import = Constraint(model.H2TerminalsOfNode, model.Period, rule=lifetime_rule_H2import)
    
    # CO2 pipeline lifetime constraint
    def co2_pipeline_lifetime_rule(model, n1, n2, i):
        """Link CO2 pipeline investments over time to installed capacity."""
        startPeriod = 1
        if value(1 + i - model.CO2PipelineLifetime / LeapYearsInvestment) > startPeriod:
            startPeriod = value(1 + i - model.CO2PipelineLifetime / LeapYearsInvestment)
        return sum(model.CO2PipelineBuilt[n1, n2, j] for j in model.Period if j >= startPeriod and j <= i) - \
               model.totalCO2PipelineCapacity[n1, n2, i] == 0
    model.co2_pipeline_lifetime = Constraint(model.CO2BidirectionalPipelines, model.Period,
                                            rule=co2_pipeline_lifetime_rule)
    
    # CO2 sequestration capacity constraint
    def co2_sequestering_max_yearly_capacity_rule(model, n, i):
        """Limit cumulative CO2 sequestration capacity development."""
        return sum(model.CO2SiteCapacityDeveloped[n, j] for j in range(1, i + 1)) <= \
               model.CO2StorageMaxHourlyCapacity[n, i]
    model.co2_sequestering_max_installed_capacity = Constraint(model.CO2SequestrationNodes, model.Period, 
                                                               rule=co2_sequestering_max_yearly_capacity_rule)
