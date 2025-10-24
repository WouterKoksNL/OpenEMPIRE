from pyomo.environ import value, ConcreteModel, Expression

def create_scenario_cut(
        mp_instance: ConcreteModel,
        sp_instance: ConcreteModel,
        capacity_params: dict[str, dict[tuple, float]],
        period_active: int,
        scenario: str,
        ) -> Expression:
    """Create a Benders optimality cut for a given scenario and period based on the dual values of the subproblem, 
    and the coefficients of the capacity variables in the subproblem constraints.
    """
    expr = value(sp_instance.Obj)
    
    # maxGenProduction
    if hasattr(sp_instance, 'maxGenProduction'):
        expr += sum(
            sum(
                sp_instance.genCapAvail[n, g, h, period_active, scenario] *
                sp_instance.dual[sp_instance.maxGenProduction[n, g, h, period_active, scenario]]
                for h in sp_instance.Operationalhour
                )
            * 
            (mp_instance.genInstalledCap[n, g, period_active] -
            value(capacity_params['genInstalledCap'][(n, g, period_active)]))
            for n, g in sp_instance.GeneratorsOfNode
        )

    # ramping
    if hasattr(sp_instance, 'ramping'):
        expr += sum(
            sum(
                sp_instance.genRampUpCap[g] *
                sp_instance.dual[sp_instance.ramping[n, g, h, period_active, scenario]]
                for h in sp_instance.Operationalhour
                if h not in sp_instance.FirstHoursOfRegSeason and h not in sp_instance.FirstHoursOfPeakSeason
                )
            * 
            (mp_instance.genInstalledCap[n, g, period_active] -
            value(capacity_params['genInstalledCap'][(n, g, period_active)]))
            for n, g in sp_instance.GeneratorsOfNode
            if g in sp_instance.ThermalGenerators
        )

    # storage_operational_cap
    if hasattr(sp_instance, 'storage_operational_cap'):
        expr += sum(
            sum(
                sp_instance.dual[sp_instance.storage_operational_cap[n, b, h, period_active, scenario]]
                for h in sp_instance.Operationalhour
                )
            * 
            (mp_instance.storENInstalledCap[n, b, period_active] -
            value(capacity_params['storENInstalledCap'][(n, b, period_active)]))
            for n, b in sp_instance.StoragesOfNode
        )
        
    # storage_energy_balance
    if hasattr(sp_instance, 'storage_energy_balance_upper'):
        expr += sum(
            sum(
                sp_instance.storOperationalInit[b] *
                sp_instance.dual[sp_instance.storage_energy_balance_upper[n, b, h, period_active, scenario]]
                for h in sp_instance.Operationalhour
                if h in sp_instance.FirstHoursOfRegSeason or h in sp_instance.FirstHoursOfPeakSeason
                )
            *
            (mp_instance.storENInstalledCap[n, b, period_active] -
            value(capacity_params['storENInstalledCap'][(n, b, period_active)]))
            for n, b in sp_instance.StoragesOfNode
        )

    if hasattr(sp_instance, 'storage_energy_balance_lower'):
        expr += sum(
            sum(
                -sp_instance.storOperationalInit[b] *
                sp_instance.dual[sp_instance.storage_energy_balance_lower[n, b, h, period_active, scenario]]
                for h in sp_instance.Operationalhour
                if h in sp_instance.FirstHoursOfRegSeason or h in sp_instance.FirstHoursOfPeakSeason
                )
            *
            (mp_instance.storENInstalledCap[n, b, period_active] -
            value(capacity_params['storENInstalledCap'][(n, b, period_active)]))
            for n, b in sp_instance.StoragesOfNode
        )

    # storage_seasonal_net_zero_balance
    if hasattr(sp_instance, 'storage_seasonal_net_zero_balance'):
        expr += sum(
            sum(
                -sp_instance.storOperationalInit[b] *
                sp_instance.dual[sp_instance.storage_seasonal_net_zero_balance[n, b, h, period_active, scenario]]
                for h in sp_instance.Operationalhour
                if h in sp_instance.FirstHoursOfRegSeason or h in sp_instance.FirstHoursOfPeakSeason
                )
            *
            (mp_instance.storENInstalledCap[n, b, period_active] -
            value(capacity_params['storENInstalledCap'][(n, b, period_active)]))
            for n, b in sp_instance.StoragesOfNode
        )

    # storage_power_charg_cap
    if hasattr(sp_instance, 'storage_power_charg_cap'):
        expr += sum(
            sum(
                sp_instance.dual[sp_instance.storage_power_charg_cap[n, b, h, period_active, scenario]]
                for h in sp_instance.Operationalhour
                )
            * 
            (mp_instance.storPWInstalledCap[n, b, period_active] -
            value(capacity_params['storPWInstalledCap'][(n, b, period_active)]))
            for n, b in sp_instance.StoragesOfNode
        )

    # storage_power_discharg_cap
    if hasattr(sp_instance, 'storage_power_discharg_cap'):
        expr += sum(
            sum(
                sp_instance.storageDiscToCharRatio[b] *
                sp_instance.dual[sp_instance.storage_power_discharg_cap[n, b, h, period_active, scenario]]
                for h in sp_instance.Operationalhour
                )
            *
            (mp_instance.storPWInstalledCap[n, b, period_active] -
            value(capacity_params['storPWInstalledCap'][(n, b, period_active)]))
            for n, b in sp_instance.StoragesOfNode
        )

    # transmission_cap
    if hasattr(sp_instance, 'transmission_cap'):
        for n1, n2 in sp_instance.DirectionalLink:
                if (n1, n2) in sp_instance.BidirectionalArc:
                    inds = (n1, n2, period_active)
                elif (n2, n1) in sp_instance.BidirectionalArc:
                    inds = (n2, n1, period_active)
                else:
                    raise ValueError("Transmission capacity indices not found in old capacities.")
                expr += sum(
                    sp_instance.dual[sp_instance.transmission_cap[n1, n2, h, period_active, scenario]]
                    for h in sp_instance.Operationalhour
                    ) * (mp_instance.transmissionInstalledCap[inds] -
                        value(capacity_params['transmissionInstalledCap'][inds]))
        
    return  mp_instance.theta[period_active, scenario] >= expr


