from pyomo.environ import Set


def define_shared_offshore_converter_derived_sets(model, offshoreNodesList):
    # Offshore energy hubs
    def OffshoreEnergyHubs_init(model):
        retval = []
        for node in model.Node:
            if node in offshoreNodesList:
                retval.append(node)
        return retval
    model.OffshoreEnergyHubs = Set(initialize=OffshoreEnergyHubs_init, ordered=True)