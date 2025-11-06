# Helper for copula-based SGR
COPULA_TO_LABEL_MAPPING = dict({
    "windonshore": "Wind onshore",
    "electricload": "Load",
    "solar": "Solar PV",
    "hydroror": "Hydrorun-of-the-river",
})

class Constants:
    ng_MWhPerTon = 13.9  # MJ per standard cubic meter of NG * cubic meter per MWh / MJ per ton
    GJperMWh = 3.6
    hydrogen_MWhPerTon = 33.3
    coal_lhv_mj_per_kg = 29.0 # MJ/kg = GJ/ton
    co2_scale_factor = 1

