from pyomo.environ import Param, NonNegativeReals


def define_hydrogen_investments_as_param(model):
    """Define hydrogen investment variables as parameters for out-of-sample runs."""
    # Hydrogen import terminal investments
    model.H2ImportCapBuilt = Param(model.H2TerminalsOfNode, model.Period, domain=NonNegativeReals)
    model.H2ImportTotalCap = Param(model.H2TerminalsOfNode, model.Period, domain=NonNegativeReals)

    # Electrolyzer investments
    model.elyzerCapBuilt = Param(model.HydrogenProdNode, model.Period, domain=NonNegativeReals)
    model.elyzerTotalCap = Param(model.HydrogenProdNode, model.Period, domain=NonNegativeReals)
    
    # Reformer investments
    model.ReformerCapBuilt = Param(model.ReformerLocations, model.ReformerPlants, model.Period, domain=NonNegativeReals)
    model.ReformerTotalCap = Param(model.ReformerLocations, model.ReformerPlants, model.Period, domain=NonNegativeReals)
    
    # Hydrogen pipeline investments
    model.hydrogenPipelineBuilt = Param(model.HydrogenBidirectionPipelines, model.Period, domain=NonNegativeReals)
    model.repurposedPipelineBuilt = Param(model.RepurposeDirectionalLinks, model.Period, domain=NonNegativeReals)
    model.totalHydrogenPipelineCapacity = Param(model.HydrogenBidirectionPipelines, model.Period, domain=NonNegativeReals)
    
    # Hydrogen storage investments
    model.hydrogenStorageBuilt = Param(model.HydrogenProdNode, model.H2Storages, model.Period, domain=NonNegativeReals)
    model.hydrogenTotalStorage = Param(model.HydrogenProdNode, model.H2Storages, model.Period, domain=NonNegativeReals)

    # CO2 infrastructure investments
    model.CO2PipelineBuilt = Param(model.CO2BidirectionalPipelines, model.Period, domain=NonNegativeReals)
    model.totalCO2PipelineCapacity = Param(model.CO2BidirectionalPipelines, model.Period, domain=NonNegativeReals)
    model.CO2SiteCapacityDeveloped = Param(model.CO2SequestrationNodes, model.Period, domain=NonNegativeReals)


def load_hydrogen_oos_investments(model, data, result_file_path):
    """Load hydrogen module investment decisions from in-sample runs as parameters for out-of-sample run."""
    # Load hydrogen import terminal data
    data.load(filename=str(result_file_path + "/" + 'H2ImportCapBuilt.tab'), param=model.H2ImportCapBuilt, format="table")
    data.load(filename=str(result_file_path + "/" + 'H2ImportTotalCap.tab'), param=model.H2ImportTotalCap, format="table")

    # Load electrolyzer data
    data.load(filename=str(result_file_path + "/" + 'elyzerCapBuilt.tab'), param=model.elyzerCapBuilt, format="table")
    data.load(filename=str(result_file_path + "/" + 'elyzerTotalCap.tab'), param=model.elyzerTotalCap, format="table")
    
    # Load reformer data
    data.load(filename=str(result_file_path + "/" + 'ReformerCapBuilt.tab'), param=model.ReformerCapBuilt, format="table")
    data.load(filename=str(result_file_path + "/" + 'ReformerTotalCap.tab'), param=model.ReformerTotalCap, format="table")
    
    # Load hydrogen pipeline data
    data.load(filename=str(result_file_path + "/" + 'hydrogenPipelineBuilt.tab'), param=model.hydrogenPipelineBuilt, format="table")
    data.load(filename=str(result_file_path + "/" + 'repurposedPipelineBuilt.tab'), param=model.repurposedPipelineBuilt, format="table")
    data.load(filename=str(result_file_path + "/" + 'totalHydrogenPipelineCapacity.tab'), param=model.totalHydrogenPipelineCapacity, format="table")
    
    # Load hydrogen storage data
    data.load(filename=str(result_file_path + "/" + 'hydrogenStorageBuilt.tab'), param=model.hydrogenStorageBuilt, format="table")
    data.load(filename=str(result_file_path + "/" + 'hydrogenTotalStorage.tab'), param=model.hydrogenTotalStorage, format="table")

    # Load CO2 infrastructure data
    data.load(filename=str(result_file_path + "/" + 'CO2PipelineBuilt.tab'), param=model.CO2PipelineBuilt, format="table")
    data.load(filename=str(result_file_path + "/" + 'totalCO2PipelineCapacity.tab'), param=model.totalCO2PipelineCapacity, format="table")
    data.load(filename=str(result_file_path + "/" + 'CO2SiteCapacityDeveloped.tab'), param=model.CO2SiteCapacityDeveloped, format="table")
