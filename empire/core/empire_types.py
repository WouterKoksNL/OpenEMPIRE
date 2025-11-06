from dataclasses import dataclass


@dataclass
class Flags:
    natural_gas: bool
    heat: bool
    hydrogen: bool
    industry: bool
    cvar: bool
    gas_stochasticity: bool
    out_of_sample: bool