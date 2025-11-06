from pyomo.environ import Var, NonNegativeReals, AbstractModel


def define_hydrogen_investment_variables(model: AbstractModel):
    """Define hydrogen investment decision variables."""
    # Hydrogen import terminal investments
    model.H2ImportCapBuilt = Var(model.H2TerminalsOfNode, model.Period, domain=NonNegativeReals)
    model.H2ImportTotalCap = Var(model.H2TerminalsOfNode, model.Period, domain=NonNegativeReals)

    # Electrolyzer investments
    model.elyzerCapBuilt = Var(model.HydrogenProdNode, model.Period, domain=NonNegativeReals)
    model.elyzerTotalCap = Var(model.HydrogenProdNode, model.Period, domain=NonNegativeReals)
    
    # Reformer investments
    model.ReformerCapBuilt = Var(model.ReformerLocations, model.ReformerPlants, model.Period, domain=NonNegativeReals)  # Capacity of MW H2 production built in period i
    model.ReformerTotalCap = Var(model.ReformerLocations, model.ReformerPlants, model.Period, domain=NonNegativeReals)  # Total capacity of MW H2 production
    
    # Hydrogen pipeline investments
    model.hydrogenPipelineBuilt = Var(model.HydrogenBidirectionPipelines, model.Period, domain=NonNegativeReals)
    model.repurposedPipelineBuilt = Var(model.RepurposeDirectionalLinks, model.Period, domain=NonNegativeReals)
    model.totalHydrogenPipelineCapacity = Var(model.HydrogenBidirectionPipelines, model.Period, domain=NonNegativeReals)
    
    # Hydrogen storage investments
    model.hydrogenStorageBuilt = Var(model.HydrogenProdNode, model.H2Storages, model.Period, domain=NonNegativeReals)
    model.hydrogenTotalStorage = Var(model.HydrogenProdNode, model.H2Storages, model.Period, domain=NonNegativeReals)

    # CO2 infrastructure investments
    model.CO2PipelineBuilt = Var(model.CO2BidirectionalPipelines, model.Period, domain=NonNegativeReals)
    model.totalCO2PipelineCapacity = Var(model.CO2BidirectionalPipelines, model.Period, domain=NonNegativeReals)
    model.CO2SiteCapacityDeveloped = Var(model.CO2SequestrationNodes, model.Period, domain=NonNegativeReals)
