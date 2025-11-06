from inspect import Parameter, signature
from pathlib import Path
from typing import Dict
from dataclasses import dataclass
import yaml


def read_config_file(path: Path) -> Dict:
    with open(path) as file:
        config = yaml.safe_load(file)

    return config


class EmpireConfiguration:
    def __init__(
        self,
        # General settings
        use_temporary_directory: bool,
        temporary_directory: str | Path,
        forecast_horizon_year: int,
        time_format: str = "%d/%m/%Y %H:%M",
        optimization_solver: str = "Gurobi",

        # Financial parameters
        discount_rate: float = 0.05,
        wacc: float = 0.05,

        # Sampling parameters
        use_default_timeseries_source: bool = True,
        fixed_sampling_key_flag: bool = False,
        fixed_csv_sample_flag: bool = False,
        filter_make: bool = False,
        filter_use: bool = False,
        n_cluster: int = 10,
        moment_matching: bool = False,
        copula_clusters_make: bool = False,
        copula_clusters_use: bool = False,
        copulas_to_use: list[str] = [],
        n_tree_compare: int = 10,

        # Operational parameters 
        regular_seasons: list[str] = ["winter", "spring", "summer", "fall"],
        n_peak_seasons: int = 2,
        length_peak_season: int = 24,
        leap_years_investment: int = 5,
        number_of_scenarios: int = 10,
        length_regular_season: int = 24 * 7,

        # Flags
        benders_flag: bool = False,
        cvar_flag: bool = False,
        hydrogen_flag: bool = False,
        heat_flag: bool = False,
        industry_flag: bool = False,
        industry_flexibility_flag: bool = False,
        emission_cap_flag: bool = True,
        compute_operational_duals_flag: bool = False,
        print_iamc_flag: bool = False,
        write_in_lp_format: bool = False,
        serialize_instance: bool = False,
        north_sea_flag: bool = True,
        pickle_instance_flag: bool = False,

        # Voronoi SGR
        voronoi_sgr_make: bool = False,
        voronoi_sgr_use: bool = False,
        voronoi_mu_percentile: int = 80,
        
        max_benders_iterations: int = 50,
        parallel_benders_flag: bool = False,
        n_cores: int = 4,
        include_hydro_node_limit_constraint_flag: bool = True,
        
        # Risk parameters
        cvar_percentile: float = 0.95,
        cvar_weight: float = 0.0,

        # Industry parameters
        steel_CCS_capture_rate: float | None = 0.9,
        steel_CCS_cost_increase: float | None = 1.,

        # Hydrogen parameters
        gas_h2_repurpose_cost_factor: float | None = 0.25,
        repurposeEnergyFlowFactor: float | None = 0.8,

        **kwargs,
    ):
        """
        Class containing configurations for running Empire simulations.

        :param use_temporary_directory: Specifies whether to use a temporary directory for operations.
        :param temporary_directory: Path to the temporary directory used for certain operations.
        :param forecast_horizon_year: The last strategic (investment) period used in the optimization run. NB! Must correspond with data for version.
        :param number_of_scenarios: The number of scenarios in every investment period.
        :param length_regular_season: The number of chronological time steps in a regular season. NB! Must correspond with data for version.
        :param discount_rate: Rate used to discount future cash flows to present value.
        :param wacc: The Weighted Average Cost of Capital (WACC).
        :param optimization_solver: Mathematical solver used for optimization tasks. Options: “Xpress”, “Gurobi”, “CPLEX”.
        :param use_fixed_sample: If true, operational scenarios will be generated according to a fixed sampling key located in the ‘Scenario Data’ folder to ensure the same operational scenarios are generated.
        :param filter_make:
        :param filter_use:
        :param n_cluster:
        :param moment_matching:
        :param n_tree_compare:
        :param emission_cap_flag: If true, emissions in every scenario are capped according to the specified cap in ‘General.xlsx’. If false, the CO2-price specified in ‘General.xlsx’ applies.
        :param compute_operational_duals: If true, investment decisions are fixed and resolved to compute operational duals
        :param print_in_iamc_format: OIf true, selected results are printed on the standard IAMC-format in addition to the normal EMPIRE print.
        :param write_in_lp_format: Problem should be written in Linear Programming format.
        :param serialize_instance: Serialize the data structure or model for later use.
        :param north_sea_flag: Whether north-sea is modelled or not.
        :param regular_seasons: Regular seasons.
        :param n_peak_seasons:  Peak seasons.
        :param leap_years_investment: Years between investment decisions
        :param time_format: Time format

        """

        # ------------------------------
        # General settings
        # ------------------------------
        self.use_temporary_directory = use_temporary_directory
        self.temporary_directory = Path(temporary_directory).absolute()
        self.forecast_horizon_year = forecast_horizon_year
        self.time_format = time_format
        self.optimization_solver = optimization_solver

        # ------------------------------
        # Financial parameters
        # ------------------------------
        self.discount_rate = discount_rate
        self.wacc = wacc

        # ------------------------------
        # Sampling parameters
        # ------------------------------
        self.use_default_timeseries_source = use_default_timeseries_source
        self.fixed_sampling_key_flag = fixed_sampling_key_flag
        self.fixed_csv_sample_flag = fixed_csv_sample_flag
        self.filter_make = filter_make
        self.filter_use = filter_use
        self.n_cluster = n_cluster
        self.moment_matching = moment_matching
        self.copula_clusters_make = copula_clusters_make
        self.copula_clusters_use = copula_clusters_use
        self.copulas_to_use = copulas_to_use
        self.n_tree_compare = n_tree_compare

        # ------------------------------
        # Operational parameters
        # ------------------------------
        self.regular_seasons = regular_seasons
        self.n_peak_seasons = n_peak_seasons
        self.length_peak_season = length_peak_season
        self.leap_years_investment = leap_years_investment
        self.number_of_scenarios = number_of_scenarios
        self.length_regular_season = length_regular_season

        # ------------------------------
        # Flags
        # ------------------------------
        self.benders_flag = benders_flag
        self.cvar_flag = cvar_flag
        self.hydrogen_flag = hydrogen_flag
        self.heat_flag = heat_flag
        self.industry_flag = industry_flag
        self.industry_flexibility_flag = industry_flexibility_flag
        self.emission_cap_flag = emission_cap_flag
        self.compute_operational_duals_flag = compute_operational_duals_flag
        self.print_iamc_flag = print_iamc_flag
        self.write_in_lp_format = write_in_lp_format
        self.serialize_instance = serialize_instance
        self.north_sea_flag = north_sea_flag
        self.pickle_instance_flag = pickle_instance_flag

        # ------------------------------
        # Voronoi SGR
        # ------------------------------
        self.voronoi_sgr_make = voronoi_sgr_make
        self.voronoi_sgr_use = voronoi_sgr_use
        self.voronoi_mu_percentile = voronoi_mu_percentile
        self.max_benders_iterations = max_benders_iterations
        self.parallel_benders_flag = parallel_benders_flag
        self.n_cores = n_cores
        self.include_hydro_node_limit_constraint_flag = include_hydro_node_limit_constraint_flag

        # ------------------------------
        # Risk parameters
        # ------------------------------
        self.cvar_percentile = cvar_percentile
        self.cvar_weight = cvar_weight

        # ------------------------------
        # Industry parameters
        # ------------------------------
        self.steel_CCS_capture_rate = steel_CCS_capture_rate
        self.steel_CCS_cost_increase = steel_CCS_cost_increase

        # ------------------------------
        # Hydrogen parameters
        # ------------------------------
        self.gas_h2_repurpose_cost_factor = gas_h2_repurpose_cost_factor
        self.repurposeEnergyFlowFactor = repurposeEnergyFlowFactor
        # ------------------------------
        # Computed attributes
        # ------------------------------
        self.n_reg_season = len(regular_seasons)
        self.periods = [i + 1 for i in range(int((self.forecast_horizon_year - 2020) / self.leap_years_investment))]
        self.n_periods = len(self.periods)

        # ------------------------------
        # Validation
        # ------------------------------
        self.validate()


    def validate(self):
        """
        Validates the configuration. Raises an error if the configuration is invalid.
        """
        pass

    @classmethod
    def from_dict(cls, config: Dict) -> "EmpireConfiguration":
        """
        Constructs EmpireConfiguration object from a dictionary.

        If constructor arguments are missing and they don't have default values,
        they are added with None value to handle earlier versions of the configuration.

        :param config: Dictionary with configurations.
        :returns: An instance of EmpireConfiguration.
        """
        # Get the signature of the __init__ method
        init_signature = signature(cls.__init__)

        # Prepare a dictionary of arguments
        # Set to None if there is no default value
        init_args: dict = {}
        for param_name, param in init_signature.parameters.items():
            if param_name != "self":
                # Check if the parameter has a default value
                if param.default is Parameter.empty:
                    init_args[param_name] = None
                else:
                    init_args[param_name] = param.default

        # Update the dictionary with values from the config
        init_args.update({k: v for k, v in config.items() if k in init_args})

        # Create an instance of the class with the arguments
        return cls(**init_args)
    
    def to_dict(self) -> dict:
        """
        Used for serialization.

        :return: dictionary
        """
        my_dict = self.__dict__
        for k in my_dict:
            if isinstance(my_dict[k], Path):
                my_dict[k] = str(my_dict[k])
                
        return my_dict

