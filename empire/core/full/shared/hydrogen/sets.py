"""Hydrogen-specific sets for the EMPIRE model."""
from pyomo.environ import Set, BuildAction
from pathlib import Path

from empire.core.loading_utils import load_sets

def define_hydrogen_sets(model):
    """Define sets specific to the hydrogen module.
    
    Args:
        model: Pyomo abstract model
    """
    
    # Hydrogen production and storage sets
    model.HydrogenProdNode = Set(ordered=True, within=model.Node)
    model.H2Storages = Set(ordered=True)
    model.ReformerLocations = Set(ordered=True, within=model.HydrogenProdNode)
    model.ReformerPlants = Set(ordered=True)
    
    # Hydrogen import sets
    model.H2Terminals = Set(ordered=True)
    model.H2TerminalNodes = Set(ordered=True, within=model.HydrogenProdNode)
    model.H2TerminalsOfNode = Set(dimen=2, ordered=True, within=model.H2TerminalNodes * model.H2Terminals)
    
    # CO2 sequestration sets
    model.CO2SequestrationNodes = Set(within=model.Node)


def load_hydrogen_set_data(data, dataset_dir: Path, model):
    """Load hydrogen set data from tab files.
    
    Args:
        data: Pyomo DataPortal object
        dataset_dir: Path to dataset input directory
        model: Pyomo model with sets already defined
    """
    # Hydrogen terminal sets

    hydrogen_sets = [
        'H2Terminals',
        'H2TerminalNodes',
        'H2TerminalsOfNode',
        'H2Storages',
        'HydrogenProdNode',
        'ReformerLocations',
        'ReformerPlants',
        'CO2SequestrationNodes',
    ]
    load_sets(data, model, dataset_dir, hydrogen_sets, component='Hydrogen')


def define_hydrogen_derived_sets(model):
    """Define derived sets that depend on other sets being loaded first.
    
    This should be called after data loading.
    
    Args:
        model: Pyomo abstract model
    """
    
    # Build hydrogen generators set
    def prep_hydrogenGenerators_rule(model):
        for g in model.Generator:
            if "hydrogen" in g.lower():
                model.HydrogenGenerators.add(g)
    model.build_hydrogenGenerators = BuildAction(rule=prep_hydrogenGenerators_rule)
    
    # Hydrogen pipeline links
    def HydrogenLinks_init(model):
        retval = []
        for (n1, n2) in model.DirectionalLink:
            if n1 in model.HydrogenProdNode and n2 in model.HydrogenProdNode:
                retval.append((n1, n2))
        return retval
    model.AllowedHydrogenLinks = Set(dimen=2, initialize=HydrogenLinks_init, ordered=True)
    
    def HydrogenBidirectionPipelines_init(model):
        retval = []
        for (n1, n2) in model.BidirectionalArc:
            if n1 in model.HydrogenProdNode and n2 in model.HydrogenProdNode:
                retval.append((n1, n2))
        return retval
    model.HydrogenBidirectionPipelines = Set(dimen=2, initialize=HydrogenBidirectionPipelines_init, ordered=True)
    
    def RepurposeDirectionalLinks_init(model):
        retval = []
        for (n1, n2) in model.HydrogenBidirectionPipelines:
            if (n1, n2) in model.NaturalGasDirectionalLink:
                retval.append((n1, n2))
            if (n2, n1) in model.NaturalGasDirectionalLink:
                retval.append((n2, n1))
        return retval
    model.RepurposeDirectionalLinks = Set(dimen=2, initialize=RepurposeDirectionalLinks_init, ordered=True)
    
    def HydrogenLinks_init(model, node):
        retval = []
        for (i, j) in model.AllowedHydrogenLinks:
            if j == node:
                retval.append(i)
        return retval
    model.HydrogenLinks = Set(model.Node, initialize=HydrogenLinks_init)
    
    # CO2 pipeline sets
    def CO2DirectionalLinks_init(model):
        retval = []
        for (n1, n2) in model.DirectionalLink:
            if n1 in model.OnshoreNode and n2 in model.OnshoreNode:
                retval.append((n1, n2))
        return retval
    model.CO2DirectionalLinks = Set(dimen=2, initialize=CO2DirectionalLinks_init, ordered=True)
    
    def CO2BidirectionalPipelines_init(model):
        retval = []
        for (n1, n2) in model.BidirectionalArc:
            if n1 in model.OnshoreNode and n2 in model.OnshoreNode:
                retval.append((n1, n2))
        return retval
    model.CO2BidirectionalPipelines = Set(dimen=2, initialize=CO2BidirectionalPipelines_init, ordered=True)
    
    def CO2Links_init(model, node):
        retval = []
        for (i, j) in model.AllowedHydrogenLinks:
            if i in model.OnshoreNode and j in model.OnshoreNode:
                if j == node:
                    retval.append(i)
        return retval
    model.CO2Links = Set(model.Node, initialize=CO2Links_init)
