"""Heat module-specific sets for the EMPIRE model."""
from pyomo.environ import Set, BuildAction


def define_heat_sets(model):
    """Define sets specific to the heat module.
    
    Args:
        model: Pyomo abstract model
    """
    
    # Converter sets
    model.Converter = Set()  # r
    model.ConverterOfNode = Set(dimen=2)  # (n,r) for all n in N, r in R_n
    
    # Generator sets for heat
    model.GeneratorCHP = Set(ordered=True)
    model.GeneratorTR = Set(ordered=True)  # G_TR
    model.GeneratorTR_Industrial = Set(ordered=True)  # G_TR_HT
    
    # Storage sets for heat
    model.StorageTR = Set(ordered=True)  # B_TR
    model.DependentStorageTR = Set()
    
    # Other heat sets
    model.RampingGeneratorsHeat = Set()
    model.TechnologyHeat = Set()
    model.StoragesOfNodeHeat = Set(dimen=2)
    model.GeneratorsOfNodeHeat = Set(dimen=2)
    model.GeneratorsOfTechnologyHeat = Set(dimen=2)




def load_heat_set_data(data, tab_file_path, model):
    """Load heat module set data from tab files.
    
    Args:
        data: Pyomo DataPortal object
        tab_file_path: Path to directory containing tab files
        model: Pyomo model with sets already defined
    """
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleSets_ElectrToHeatConverter.tab', format="set", set=model.Converter)
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleSets_ConverterOfNodes.tab', format="set", set=model.ConverterOfNode)
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleSets_GeneratorHeatAndElectricity.tab', format="set", set=model.GeneratorCHP)
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleSets_GeneratorHeat.tab', format="set", set=model.GeneratorTR)
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleSets_StorageHeat.tab', format="set", set=model.StorageTR)
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleSets_DependentStorageHeat.tab', format="set", set=model.DependentStorageTR)
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleSets_RampingGenerators.tab', format="set", set=model.RampingGeneratorsHeat)
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleSets_IndustrialHeat.tab', format="set", set=model.GeneratorTR_Industrial)
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleSets_TechnologyHeat.tab', format="set", set=model.TechnologyHeat)
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleSets_StorageOfNodes.tab', format="set", set=model.StoragesOfNodeHeat)
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleSets_GeneratorsOfNode.tab', format="set", set=model.GeneratorsOfNodeHeat)
    data.load(filename=tab_file_path + "/" + 'HeatModule/HeatModuleSets_GeneratorsOfTechnology.tab', format="set", set=model.GeneratorsOfTechnologyHeat)


def define_heat_derived_sets(model):
    """Define derived heat sets and integrate with main sets.
    
    This should be called after data loading.
    
    Args:
        model: Pyomo abstract model
    """
    
    # Define electricity-only generators and storages
    def GeneratorEL_init(model):
        retval = []
        for g in model.Generator:
            retval.append(g)
        return retval
    model.GeneratorEL = Set(within=model.Generator, initialize=GeneratorEL_init)  # G_EL
    
    def StorageEL_init(model):
        retval = []
        for g in model.Storage:
            retval.append(g)
        return retval
    model.StorageEL = Set(within=model.Storage, initialize=StorageEL_init)  # B_EL
    
    # Integrate heat module sets into main sets
    def prepSetsHeatModule_rule(model):
        for g in model.GeneratorTR:
            model.Generator.add(g)
        for g in model.GeneratorTR_Industrial:
            model.Generator.add(g)
        for g in model.GeneratorCHP:
            model.GeneratorEL.add(g)
        for g in model.RampingGeneratorsHeat:
            model.RampingGenerators.add(g)
        for b in model.StorageTR:
            model.Storage.add(b)
        for b in model.DependentStorageTR:
            model.DependentStorage.add(b)
        for t in model.TechnologyHeat:
            model.Technology.add(t)
        for nb in model.StoragesOfNodeHeat:
            model.StoragesOfNode.add(nb)
        for ng in model.GeneratorsOfNodeHeat:
            model.GeneratorsOfNode.add(ng)
        for tg in model.GeneratorsOfTechnologyHeat:
            model.GeneratorsOfTechnology.add(tg)
    model.build_SetsHeatModule = BuildAction(rule=prepSetsHeatModule_rule)
