"""Natural gas-specific sets for the EMPIRE model."""
from pyomo.environ import Set

from empire.core.loading_utils import load_sets

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


def load_natural_gas_set_data(data, dataset_dir, model):
    input_sets = [
        "NaturalGasNode",
        "NaturalGasTerminals",
        "NaturalGasTerminalsOfNode",
        "NaturalGasDirectionalLink",
    ]

    load_sets(data, model, dataset_dir, input_sets)
    return 


def define_natural_gas_derived_sets(model):
    # Natural gas generators
    def NaturalGasGenerators_init(model):
        retval = []
        for gen in model.Generator:
            if 'gas' in gen.lower():
                retval.append(gen)
        return retval
    model.NaturalGasGenerators = Set(ordered=True, initialize=NaturalGasGenerators_init, within=model.Generator)

