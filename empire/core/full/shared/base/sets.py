"""Shared sets used across investment and operational modules."""
from pyomo.environ import Set
from empire.core.loading_utils import load_sets, load_set_directly

def define_base_shared_sets(model, windfarmNodes=None):
    """Define sets that are shared across investment and operational modules.
    
    Args:
        model: Pyomo abstract model
        windfarmNodes: List of windfarm nodes (optional)
    """
    
    # Temporal sets
    model.Period = Set(ordered=True)  # i

    # Spatial sets - basic
    model.Node = Set(ordered=True)  # n
    model.OnshoreNode = Set(within=model.Node, ordered=True)
    model.DirectionalLink = Set(dimen=2, within=model.Node*model.Node, ordered=True)  # a

    model.TransmissionType = Set(ordered=True)
    
    # Technology sets
    model.Generator = Set(ordered=True)  # g
    model.HydrogenGenerators = Set(ordered=True, within=model.Generator)
    model.Technology = Set(ordered=True)  # t
    model.Storage = Set()  # b
    

    
    # Subsets
    model.GeneratorsOfTechnology = Set(dimen=2)  # (t,g) for all t in T, g in G_t
    model.GeneratorsOfNode = Set(dimen=2)  # (n,g) for all n in N, g in G_n
    model.TransmissionTypeOfDirectionalLink = Set(dimen=3)  # (n1,n2,t) for all (n1,n2) in L, t in T
    model.RampingGenerators = Set(within=model.Generator)  # g_ramp
    model.RegHydroGenerator = Set(within=model.Generator)  # g_reghyd
    model.HydroGenerator = Set(within=model.Generator)  # g_hyd
    model.StoragesOfNode = Set(dimen=2)  # (n,b) for all n in N, b in B_n
    model.DependentStorage = Set()  # b_dagger
    

    # Windfarm nodes (conditional)
    if windfarmNodes is not None:
        model.windfarmNodes = Set(ordered=True, within=model.Node, 
                                 initialize=lambda m: [n for n in windfarmNodes if n in m.Node])
    



def load_base_shared_set_data(data, dataset_dir, model, load_period=True, periods_active=None):

    input_sets = [
        "Generator",
        "RampingGenerators",
        "HydroGenerator",
        "RegHydroGenerator",
        "Storage",
        "DependentStorage",
        "Technology",
        "Node",
        "DirectionalLink",
        "TransmissionType",
        "GeneratorsOfTechnology",
        "GeneratorsOfNode",
        "StoragesOfNode",
        "TransmissionTypeOfDirectionalLink"
    ]
    # if north_sea_flag:
    #     input_sets.append("OffshoreNode")
    

    if load_period:
        # input_sets.append("Period")
        load_set_directly(data, model.Period, periods_active)
        
    load_sets(data, model, dataset_dir, input_sets)
    return 

# def load_base_shared_set_data(data, tab_file_path, model):
#     """Load shared set data from tab files.
    
#     Args:
#         data: Pyomo DataPortal object
#         tab_file_path: Path to directory containing tab files
#         model: Pyomo model with sets already defined
#     """
#     # Technology sets
#     data.load(filename=tab_file_path + "/" + 'Sets_Generator.tab', format="set", set=model.Generator)
#     data.load(filename=tab_file_path + "/" + 'Sets_RampingGenerators.tab', format="set", set=model.RampingGenerators)
#     data.load(filename=tab_file_path + "/" + 'Sets_HydroGenerator.tab', format="set", set=model.HydroGenerator)
#     data.load(filename=tab_file_path + "/" + 'Sets_HydroGeneratorWithReservoir.tab', format="set", set=model.RegHydroGenerator)
#     data.load(filename=tab_file_path + "/" + 'Sets_Storage.tab', format="set", set=model.Storage)
#     data.load(filename=tab_file_path + "/" + 'Sets_DependentStorage.tab', format="set", set=model.DependentStorage)
#     data.load(filename=tab_file_path + "/" + 'Sets_Technology.tab', format="set", set=model.Technology)
    
#     # Spatial sets
#     data.load(filename=tab_file_path + "/" + 'Sets_Node.tab', format="set", set=model.Node)
#     data.load(filename=tab_file_path + "/" + 'Sets_OnshoreNode.tab', format="set", set=model.OnshoreNode)
#     data.load(filename=tab_file_path + "/" + 'Sets_DirectionalLines.tab', format="set", set=model.DirectionalLink)
#     data.load(filename=tab_file_path + "/" + 'Sets_LineType.tab', format="set", set=model.TransmissionType)
#     data.load(filename=tab_file_path + "/" + 'Sets_LineTypeOfDirectionalLines.tab', format="set", set=model.TransmissionTypeOfDirectionalLink)
    
#     # Technology-node relationships
#     data.load(filename=tab_file_path + "/" + 'Sets_GeneratorsOfTechnology.tab', format="set", set=model.GeneratorsOfTechnology)
#     data.load(filename=tab_file_path + "/" + 'Sets_GeneratorsOfNode.tab', format="set", set=model.GeneratorsOfNode)
#     data.load(filename=tab_file_path + "/" + 'Sets_StorageOfNodes.tab', format="set", set=model.StoragesOfNode)


def define_base_shared_derived_sets(model):
    """Define derived sets that depend on other sets being loaded first."""
    # Bidirectional transmission arcs
    def BidirectionalArc_init(model):
        retval = []
        for (i, j) in model.DirectionalLink:
            if i != j and ((j, i) not in retval):
                retval.append((i, j))
        return retval
    model.BidirectionalArc = Set(dimen=2, initialize=BidirectionalArc_init, ordered=True)  # l
    
    # Nodes linked (for transmission operations)
    def NodesLinked_init(model, node):
        retval = []
        for (i, j) in model.DirectionalLink:
            if j == node:
                retval.append(i)
        return retval
    model.NodesLinked = Set(model.Node, initialize=NodesLinked_init)
    
    
