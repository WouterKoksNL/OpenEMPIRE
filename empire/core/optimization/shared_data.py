"""Functions that initialize sets, parameters and variables that are used both in investment and operational models"""
from pyomo.environ import (Set, Param)
from .loading_utils import load_sets, load_set_directly, load_params


def define_shared_sets(model, north_sea_flag):
    model.Period = Set(ordered=True) #max period
    model.PeriodActive = Set(ordered=True) #i
    model.Technology = Set(ordered=True) #t
    model.Generator = Set(ordered=True) #g
    model.Storage =  Set() #b
    model.Node = Set(ordered=True) #n
    if north_sea_flag:
        model.OffshoreNode = Set(ordered=True, within=model.Node) #n
    model.DirectionalLink = Set(dimen=2, within=model.Node*model.Node, ordered=True) #a
    model.TransmissionType = Set(ordered=True)

    model.GeneratorsOfTechnology=Set(dimen=2) #(t,g) for all t in T, g in G_t
    model.GeneratorsOfNode = Set(dimen=2) #(n,g) for all n in N, g in G_n
    model.TransmissionTypeOfDirectionalLink = Set(dimen=3) #(n1,n2,t) for all (n1,n2) in L, t in T
    model.ThermalGenerators = Set(within=model.Generator) #g_ramp
    model.RegHydroGenerator = Set(within=model.Generator) #g_reghyd
    model.HydroGenerator = Set(within=model.Generator) #g_hyd
    model.StoragesOfNode = Set(dimen=2) #(n,b) for all n in N, b in B_n
    model.DependentStorage = Set() #b_dagger

    
    #Build arc subsets

    def NodesLinked_init(model, node):
        retval = []
        for (i,j) in model.DirectionalLink:
            if j == node:
                retval.append(i)
        return retval
    model.NodesLinked = Set(model.Node, initialize=NodesLinked_init)

    def BidirectionalArc_init(model):
        retval = []
        for (i,j) in model.DirectionalLink:
            if i != j and ((j,i) not in retval):
                retval.append((i,j))
        return retval
    model.BidirectionalArc = Set(dimen=2, initialize=BidirectionalArc_init, ordered=True) #l
    return 


def load_shared_sets(model, data, dataset_dir, north_sea_flag, load_period=True, periods_active=None):

    input_sets = [
        "Generator",
        "ThermalGenerators",
        "HydroGenerator",
        "RegHydroGenerator",
        "Storage",
        "DependentStorage",
        "Technology",
        "Node",
        "DirectionalLink",
        "TransmissionType",
        "TransmissionTypeOfDirectionalLink",
        "GeneratorsOfTechnology",
        "GeneratorsOfNode",
        "StoragesOfNode",
    ]
    if north_sea_flag:
        input_sets.append("OffshoreNode")
    

    if load_period:
        input_sets.append("Period")
        load_set_directly(data, model.PeriodActive, periods_active)
        
    load_sets(data, model, dataset_dir, input_sets)
    return 


def define_shared_parameters(model, discountrate, LeapYearsInvestment):
    model.storagePowToEnergy = Param(model.DependentStorage, default=1.0, mutable=True)
    model.discountrate = Param(initialize=discountrate) 
    model.LeapYearsInvestment = Param(initialize=LeapYearsInvestment)
    return 


def load_shared_parameters(model, data, dataset_dir):
    load_params(data, model, dataset_dir, component="Storage", param_name_list=["storagePowToEnergy"])
    return 