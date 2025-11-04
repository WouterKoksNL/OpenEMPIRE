"""Natural gas-specific sets for the EMPIRE model."""
from pyomo.environ import Set

def define_natural_gas_sets(model):
    """Define sets specific to the natural gas module.
    
    Args:
        model: Pyomo abstract model
    """
    model.NaturalGasTerminals = Set(ordered=True)
    model.NaturalGasTerminalsOfNode = Set(dimen=2, ordered=True)
    model.NaturalGasNode = Set(within=model.Node, ordered=True)  # n
    model.ThermalDemandNode = Set(within=model.Node, initialize=model.NaturalGasNode)
    model.NaturalGasDirectionalLink = Set(dimen=2, within=model.NaturalGasNode*model.NaturalGasNode, ordered=True)  # a



def load_natural_gas_set_data(data, tab_file_path, model):
    """Load natural gas set data from tab files.
    
    Args:
        data: Pyomo DataPortal object
        tab_file_path: Path to directory containing tab files
        model: Pyomo model with sets already defined
    """
    data.load(filename=tab_file_path + "/" + 'Sets_NaturalGasNodes.tab',format="set", set=model.NaturalGasNode)
    data.load(filename=tab_file_path + '/' + 'Sets_NaturalGasTerminals.tab', format='set', set=model.NaturalGasTerminals)
    data.load(filename=tab_file_path + '/' + 'Sets_NaturalGasTerminalsOfNode.tab', format='set', set=model.NaturalGasTerminalsOfNode)
    data.load(filename=tab_file_path + '/' + 'Sets_NaturalGasDirectionalLines.tab', format='set', set=model.NaturalGasDirectionalLink)

