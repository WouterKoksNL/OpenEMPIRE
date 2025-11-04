from pyomo.environ import Param, NonNegativeReals


def define_industry_investments_as_param(model):
    """Define industry investment variables as parameters for out-of-sample runs."""
    model.steelPlantBuiltCapacity = Param(model.SteelProducers, model.SteelPlants, model.Period, within=NonNegativeReals)
    model.steelPlantInstalledCapacity = Param(model.SteelProducers, model.SteelPlants, model.Period, within=NonNegativeReals)

    model.cementPlantBuiltCapacity = Param(model.CementProducers, model.CementPlants, model.Period, within=NonNegativeReals)
    model.cementPlantInstalledCapacity = Param(model.CementProducers, model.CementPlants, model.Period, within=NonNegativeReals)

    model.ammoniaPlantBuiltCapacity = Param(model.AmmoniaProducers, model.AmmoniaPlants, model.Period, within=NonNegativeReals)
    model.ammoniaPlantInstalledCapacity = Param(model.AmmoniaProducers, model.AmmoniaPlants, model.Period, within=NonNegativeReals)


def load_industry_oos_investments(model, data, result_file_path):
    """Load industry module investment decisions from in-sample runs as parameters for out-of-sample run."""
    data.load(filename=str(result_file_path + "/" + 'steelPlantBuiltCapacity.tab'), param=model.steelPlantBuiltCapacity, format="table")
    data.load(filename=str(result_file_path + "/" + 'steelPlantInstalledCapacity.tab'), param=model.steelPlantInstalledCapacity, format="table")

    data.load(filename=str(result_file_path + "/" + 'cementPlantBuiltCapacity.tab'), param=model.cementPlantBuiltCapacity, format="table")
    data.load(filename=str(result_file_path + "/" + 'cementPlantInstalledCapacity.tab'), param=model.cementPlantInstalledCapacity, format="table")

    data.load(filename=str(result_file_path + "/" + 'ammoniaPlantBuiltCapacity.tab'), param=model.ammoniaPlantBuiltCapacity, format="table")
    data.load(filename=str(result_file_path + "/" + 'ammoniaPlantInstalledCapacity.tab'), param=model.ammoniaPlantInstalledCapacity, format="table")
