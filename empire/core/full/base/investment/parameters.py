"""Investment-related parameters for the EMPIRE model."""
from pyomo.environ import Param


def define_base_investment_parameters(model, offshore_wind=True):
    """Define parameters specific to investment decisions.
    
    Args:
        model: Pyomo abstract model
    """
    
    # Generator investment parameters
    model.genCapitalCost = Param(model.Generator, model.Period, default=0, mutable=True)
    model.genFixedOMCost = Param(model.Generator, model.Period, default=0, mutable=True)
    model.genInvCost = Param(model.Generator, model.Period, default=9000000, mutable=True)
    model.genLifetime = Param(model.Generator, default=0.0, mutable=True)
    model.genRefInitCap = Param(model.GeneratorsOfNode, default=0.0, mutable=True)
    model.genScaleInitCap = Param(model.Generator, model.Period, default=0.0, mutable=True)
    model.genInitCap = Param(model.GeneratorsOfNode, model.Period, default=0.0, mutable=True)
    model.genMaxBuiltCap = Param(model.Node, model.Technology, model.Period, default=500000.0, mutable=True)
    model.genMaxInstalledCapRaw = Param(model.Node, model.Technology, default=0.0, mutable=True)
    model.genMaxInstalledCapByPeriod = Param(model.Node, model.Technology, model.Period, default=0.0, mutable=True)
    model.genMaxInstalledCap = Param(model.Node, model.Technology, model.Period, default=0.0, mutable=True)
    model.genMaxBiomethaneAvailability = Param(model.Node, model.Period, default=999999, mutable=True)
    
    # Transmission investment parameters
    model.transmissionTypeCapitalCost = Param(model.TransmissionType, model.Period, default=0, mutable=True)
    model.transmissionTypeFixedOMCost = Param(model.TransmissionType, model.Period, default=0, mutable=True)
    model.transmissionInvCost = Param(model.BidirectionalArc, model.Period, default=3000000, mutable=True)
    model.transmissionLength = Param(model.BidirectionalArc, mutable=True)
    model.transmissionInitCap = Param(model.BidirectionalArc, model.Period, default=0.0, mutable=True)
    model.transmissionMaxBuiltCap = Param(model.BidirectionalArc, model.Period, default=10000.0, mutable=True)
    model.transmissionMaxInstalledCapRaw = Param(model.BidirectionalArc, model.Period, default=0.0)
    model.transmissionMaxInstalledCap = Param(model.BidirectionalArc, model.Period, default=0.0, mutable=True)
    model.transmissionLifetime = Param(model.BidirectionalArc, default=40.0, mutable=True)
    
    # Storage investment parameters
    model.storPWCapitalCost = Param(model.Storage, model.Period, default=0, mutable=True)
    model.storENCapitalCost = Param(model.Storage, model.Period, default=0, mutable=True)
    model.storPWFixedOMCost = Param(model.Storage, model.Period, default=0, mutable=True)
    model.storENFixedOMCost = Param(model.Storage, model.Period, default=0, mutable=True)
    model.storPWInvCost = Param(model.Storage, model.Period, default=1000000, mutable=True)
    model.storENInvCost = Param(model.Storage, model.Period, default=800000, mutable=True)
    model.storPWInitCap = Param(model.StoragesOfNode, model.Period, default=0.0, mutable=True)
    model.storENInitCap = Param(model.StoragesOfNode, model.Period, default=0.0, mutable=True)
    model.storPWMaxBuiltCap = Param(model.StoragesOfNode, model.Period, default=500000.0, mutable=True)
    model.storENMaxBuiltCap = Param(model.StoragesOfNode, model.Period, default=500000.0, mutable=True)
    model.storPWMaxInstalledCap = Param(model.StoragesOfNode, model.Period, default=0.0, mutable=True)
    model.storPWMaxInstalledCapRaw = Param(model.StoragesOfNode, default=0.0, mutable=True)
    model.storENMaxInstalledCap = Param(model.StoragesOfNode, model.Period, default=0.0, mutable=True)
    model.storENMaxInstalledCapRaw = Param(model.StoragesOfNode, default=0.0, mutable=True)
    model.storageLifetime = Param(model.Storage, default=0.0, mutable=True)
    
    # Offshore converter investment parameters
    if offshore_wind:
        model.offshoreConvCapitalCost = Param(model.Period, default=999999, mutable=True)
        model.offshoreConvInvCost = Param(model.Period, default=999999, mutable=True)
        model.offshoreConvOMCost = Param(model.Period, default=999999, mutable=True)
        model.offshoreConvLifetime = Param(default=40)




def load_base_investment_parameter_data(data, tab_file_path, model, offshore_wind=True):
    """Load investment parameter data from tab files.
    
    Args:
        data: Pyomo DataPortal object
        tab_file_path: Path to directory containing tab files
        model: Pyomo model with parameters already defined
    """
    # Generator investment parameters
    data.load(filename=tab_file_path + "/" + 'Generator_CapitalCosts.tab', param=model.genCapitalCost, format="table")
    data.load(filename=tab_file_path + "/" + 'Generator_FixedOMCosts.tab', param=model.genFixedOMCost, format="table")
    data.load(filename=tab_file_path + "/" + 'Generator_RefInitialCap.tab', param=model.genRefInitCap, format="table")
    data.load(filename=tab_file_path + "/" + 'Generator_ScaleFactorInitialCap.tab', param=model.genScaleInitCap, format="table")
    data.load(filename=tab_file_path + "/" + 'Generator_InitialCapacity.tab', param=model.genInitCap, format="table")
    data.load(filename=tab_file_path + "/" + 'Generator_MaxBuiltCapacity.tab', param=model.genMaxBuiltCap, format="table")
    data.load(filename=tab_file_path + "/" + 'Generator_MaxInstalledCapacity.tab', param=model.genMaxInstalledCapRaw, format="table")
    data.load(filename=tab_file_path + "/" + 'Generator_MaxInstalledCapacityByPeriod.tab', param=model.genMaxInstalledCapByPeriod, format="table")
    data.load(filename=tab_file_path + '/' + 'Generator_MaxBiomethaneAvailability.tab', param=model.genMaxBiomethaneAvailability, format='table')
    data.load(filename=tab_file_path + "/" + 'Generator_Lifetime.tab', param=model.genLifetime, format="table")
    
    # Transmission investment parameters
    data.load(filename=tab_file_path + "/" + 'Transmission_InitialCapacity.tab', param=model.transmissionInitCap, format="table")
    data.load(filename=tab_file_path + "/" + 'Transmission_MaxBuiltCapacity.tab', param=model.transmissionMaxBuiltCap, format="table")
    data.load(filename=tab_file_path + "/" + 'Transmission_MaxInstallCapacityRaw.tab', param=model.transmissionMaxInstalledCapRaw, format="table")
    data.load(filename=tab_file_path + "/" + 'Transmission_Length.tab', param=model.transmissionLength, format="table")
    data.load(filename=tab_file_path + "/" + 'Transmission_TypeCapitalCost.tab', param=model.transmissionTypeCapitalCost, format="table")
    data.load(filename=tab_file_path + "/" + 'Transmission_TypeFixedOMCost.tab', param=model.transmissionTypeFixedOMCost, format="table")
    data.load(filename=tab_file_path + "/" + 'Transmission_Lifetime.tab', param=model.transmissionLifetime, format="table")

    
    # Storage investment parameters
    data.load(filename=tab_file_path + "/" + 'Storage_EnergyCapitalCost.tab', param=model.storENCapitalCost, format="table")
    data.load(filename=tab_file_path + "/" + 'Storage_EnergyFixedOMCost.tab', param=model.storENFixedOMCost, format="table")
    data.load(filename=tab_file_path + "/" + 'Storage_EnergyInitialCapacity.tab', param=model.storENInitCap, format="table")
    data.load(filename=tab_file_path + "/" + 'Storage_EnergyMaxBuiltCapacity.tab', param=model.storENMaxBuiltCap, format="table")
    data.load(filename=tab_file_path + "/" + 'Storage_EnergyMaxInstalledCapacity.tab', param=model.storENMaxInstalledCapRaw, format="table")
    data.load(filename=tab_file_path + "/" + 'Storage_PowerCapitalCost.tab', param=model.storPWCapitalCost, format="table")
    data.load(filename=tab_file_path + "/" + 'Storage_PowerFixedOMCost.tab', param=model.storPWFixedOMCost, format="table")
    data.load(filename=tab_file_path + "/" + 'Storage_InitialPowerCapacity.tab', param=model.storPWInitCap, format="table")
    data.load(filename=tab_file_path + "/" + 'Storage_PowerMaxBuiltCapacity.tab', param=model.storPWMaxBuiltCap, format="table")
    data.load(filename=tab_file_path + "/" + 'Storage_PowerMaxInstalledCapacity.tab', param=model.storPWMaxInstalledCapRaw, format="table")
    data.load(filename=tab_file_path + "/" + 'Storage_Lifetime.tab', param=model.storageLifetime, format="table")

    if offshore_wind:
        data.load(filename=tab_file_path + "/" + 'Transmission_OffshoreConverterCapitalCost.tab', param=model.offshoreConvCapitalCost, format="table")
        data.load(filename=tab_file_path + "/" + 'Transmission_OffshoreConverterOMCost.tab', param=model.offshoreConvOMCost, format="table")