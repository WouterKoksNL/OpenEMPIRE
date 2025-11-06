from pyomo.environ import Var, NonNegativeReals, AbstractModel


def define_hydrogen_operational_variables(model: AbstractModel):
    """Define hydrogen operational decision variables."""
    # Hydrogen import variables
    model.H2Imported_ton = Var(model.H2TerminalNodes, model.H2Terminals, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals)
    model.H2Imported_MWh = Var(model.H2TerminalNodes, model.H2Terminals, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals)

    # Hydrogen production variables
    model.hydrogenProducedElectro_ton = Var(model.HydrogenProdNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals)
    model.hydrogenProducedReformer_ton = Var(model.ReformerLocations, model.ReformerPlants, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals)
    model.hydrogenProducedReformer_MWh = Var(model.ReformerLocations, model.ReformerPlants, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals)
    
    # Hydrogen transmission variables
    model.hydrogenSentPipeline = Var(model.AllowedHydrogenLinks, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals)
    
    # Power for hydrogen production
    model.powerForHydrogen = Var(model.HydrogenProdNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals)
    
    # Natural gas for hydrogen production
    model.ng_forHydrogen = Var(model.ReformerLocations, model.ReformerPlants, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals)

    # Hydrogen storage variables
    model.hydrogenStorageOperational = Var(model.HydrogenProdNode, model.H2Storages, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals)
    model.hydrogenChargeStorage = Var(model.HydrogenProdNode, model.H2Storages, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals, initialize=0)
    model.hydrogenDischargeStorage = Var(model.HydrogenProdNode, model.H2Storages, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals, initialize=0)

    # Hydrogen for power generation
    model.hydrogenForPower = Var(model.HydrogenGenerators, model.HydrogenProdNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals, initialize=0.0)

    # CO2 transport and sequestration variables
    model.CO2sentPipeline = Var(model.CO2DirectionalLinks, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals)
    model.CO2sequestered = Var(model.CO2SequestrationNodes, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, domain=NonNegativeReals)

    # Transport sector demand variables
    model.transport_electricityDemandMet = Var(model.OnshoreNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, within=NonNegativeReals)
    model.transport_electricityDemandShed = Var(model.OnshoreNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, within=NonNegativeReals)
    model.transport_hydrogenDemandMet = Var(model.OnshoreNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, within=NonNegativeReals)
    model.transport_hydrogenDemandShed = Var(model.OnshoreNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, within=NonNegativeReals)
    model.transport_naturalGasDemandMet = Var(model.OnshoreNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, within=NonNegativeReals)
    model.transport_naturalGasDemandShed = Var(model.OnshoreNode, model.Operationalhour, model.Period, model.Scenario, model.GasScenario, within=NonNegativeReals)
