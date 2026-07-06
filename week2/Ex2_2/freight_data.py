"""
freight_data.py  —  the shared world for Week 2.

This is plain data: loads, carriers, and a distance table. Both toolsets
(the rough one you're given and the good one you'll design) read from this
exact same data, so any difference in agent behaviour comes from the TOOLS,
not the data. Don't edit this file — build your tools around it.
"""

# ---------------------------------------------------------------------------
# Distances are stored once, keyed by the two cities sorted alphabetically and
# joined with a hyphen, e.g. Mumbai + Delhi -> "Delhi-Mumbai". Use the helper
# below so you never worry about order.
# ---------------------------------------------------------------------------
DISTANCES_KM = {
    "Bangalore-Chennai": 350,
    "Bangalore-Mumbai": 980,
    "Bangalore-Pune": 840,
    "Chennai-Delhi": 2180,
    "Delhi-Hyderabad": 1580,
    "Delhi-Kolkata": 1500,
    "Delhi-Mumbai": 1420,
    "Delhi-Pune": 1430,
    "Hyderabad-Mumbai": 710,
    "Mumbai-Pune": 150,
}


def distance_key(city_a: str, city_b: str) -> str:
    """Build the canonical lookup key for a city pair (order-independent)."""
    return "-".join(sorted([city_a, city_b]))


# ---------------------------------------------------------------------------
# Carriers: who hauls the loads, and how reliable they are.
# ---------------------------------------------------------------------------
CARRIERS = {
    "CAR_01": {"name": "Sharma Logistics", "on_time_pct": 94},
    "CAR_02": {"name": "Patel Transport", "on_time_pct": 88},
    "CAR_03": {"name": "Reliable Freight", "on_time_pct": 96},
    "CAR_04": {"name": "Highway Movers", "on_time_pct": 82},
    "CAR_05": {"name": "Express Cargo", "on_time_pct": 90},
}

# ---------------------------------------------------------------------------
# Loads: the freight itself. `distance_km` is precomputed from the table above
# so each record is self-contained. status is one of:
#   pending | in_transit | delivered
# ---------------------------------------------------------------------------
LOADS = {
    "LOAD_001": {"origin": "Mumbai",    "destination": "Delhi",     "weight_tons": 8,  "status": "pending",    "carrier_id": "CAR_01", "distance_km": 1420},
    "LOAD_002": {"origin": "Pune",      "destination": "Bangalore", "weight_tons": 14, "status": "in_transit", "carrier_id": "CAR_02", "distance_km": 840},
    "LOAD_003": {"origin": "Chennai",   "destination": "Delhi",     "weight_tons": 11, "status": "pending",    "carrier_id": "CAR_03", "distance_km": 2180},
    "LOAD_004": {"origin": "Mumbai",    "destination": "Pune",      "weight_tons": 5,  "status": "delivered",  "carrier_id": "CAR_01", "distance_km": 150},
    "LOAD_005": {"origin": "Delhi",     "destination": "Kolkata",   "weight_tons": 9,  "status": "pending",    "carrier_id": "CAR_04", "distance_km": 1500},
    "LOAD_006": {"origin": "Bangalore", "destination": "Chennai",   "weight_tons": 7,  "status": "in_transit", "carrier_id": "CAR_02", "distance_km": 350},
    "LOAD_007": {"origin": "Mumbai",    "destination": "Bangalore", "weight_tons": 12, "status": "pending",    "carrier_id": "CAR_05", "distance_km": 980},
    "LOAD_008": {"origin": "Hyderabad", "destination": "Mumbai",    "weight_tons": 6,  "status": "delivered",  "carrier_id": "CAR_03", "distance_km": 710},
    "LOAD_009": {"origin": "Hyderabad", "destination": "Delhi",     "weight_tons": 15, "status": "pending",    "carrier_id": "CAR_01", "distance_km": 1580},
    "LOAD_010": {"origin": "Pune",      "destination": "Delhi",     "weight_tons": 10, "status": "in_transit", "carrier_id": "CAR_04", "distance_km": 1430},
    "LOAD_011": {"origin": "Mumbai",    "destination": "Delhi",     "weight_tons": 13, "status": "pending",    "carrier_id": "CAR_05", "distance_km": 1420},
    "LOAD_012": {"origin": "Bangalore", "destination": "Chennai",   "weight_tons": 4,  "status": "delivered",  "carrier_id": "CAR_02", "distance_km": 350},
}
