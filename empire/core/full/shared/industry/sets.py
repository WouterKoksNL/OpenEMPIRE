"""Industry-specific sets for the EMPIRE model."""
from pyomo.environ import BuildAction, Set


def define_industry_sets(model):
    model.SteelPlants = Set(ordered=True)
    model.SteelPlants_FinalSteel = Set(within=model.SteelPlants, ordered=True)
    model.CementPlants = Set(ordered=True)
    model.AmmoniaPlants = Set(ordered=True)
    model.SteelProducers = Set(within=model.Node, ordered=True)
    model.CementProducers = Set(within=model.Node, ordered=True)
    model.AmmoniaProducers = Set(within=model.Node, ordered=True)
    model.OilProducers = Set(within=model.Node, ordered=True)
    

def load_industry_set_data(data, tab_file_path, model):
    """Load industry set data from tab files.
    
    Args:
        data: Pyomo DataPortal object
        tab_file_path: Path to directory containing tab files
        model: Pyomo model with sets already defined
    """
    # Producer node sets
    data.load(filename=tab_file_path + "/" + 'Sets_SteelProducers.tab', format="set", set=model.SteelProducers)
    data.load(filename=tab_file_path + "/" + 'Sets_CementProducers.tab', format="set", set=model.CementProducers)
    data.load(filename=tab_file_path + "/" + 'Sets_AmmoniaProducers.tab', format="set", set=model.AmmoniaProducers)
    data.load(filename=tab_file_path + "/" + 'Sets_OilProducers.tab', format="set", set=model.OilProducers)
    
    # Plant type sets
    data.load(filename=tab_file_path + '/' + 'Industry_SteelProductionPlants.tab', format='set', set=model.SteelPlants)
    data.load(filename=tab_file_path + '/' + 'Industry_CementProductionPlants.tab', format='set', set=model.CementPlants)
    data.load(filename=tab_file_path + '/' + 'Industry_AmmoniaProductionPlants.tab', format='set', set=model.AmmoniaPlants)


def define_industry_derived_sets(model):
    """Define derived industry sets that depend on other sets being loaded first.
    
    This should be called after data loading.
    
    Args:
        model: Pyomo abstract model
    """
    
    # Build final steel producers set
    def prepFinalSteelProducers(model):
        for p in model.SteelPlants:
            if 'eaf' in p.lower() or 'bof' in p.lower():
                model.SteelPlants_FinalSteel.add(p)
    model.build_SteelPlants_FinalSteel = BuildAction(rule=prepFinalSteelProducers)
