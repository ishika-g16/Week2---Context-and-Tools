'''
Revised toolset with 4 functions: list_loads, get_load_details, get_distance, and sum_distances
Improved tool descriptions in tool schema 

'''

from freight_data import DISTANCES_KM, distance_key, CARRIERS, LOADS

# ------------------- TOOLS -------------------

def list_loads(origin=None, destination=None, weight_tons=None,  status=None, carrier_id=None, distance_km=None) -> str:
   out_list = []
   for load, details in LOADS.items():
      if origin and details["origin"].lower() != origin.lower(): 
         # if an origin is specified as input, but the curent load doesn't match that origin,
         # this will skip to the next load (iteration) as the current one does not fit into the filter
         continue
      if destination and details["destination"].lower() != destination.lower():
         continue
      if weight_tons and details["weight_tons"] != weight_tons:
         continue 
      if status and details["status"].lower() != status.lower():
         continue
      if carrier_id and details["carrier_id"].lower() != carrier_id.lower():
         continue
      if distance_km and details["distance_km"] != distance_km:
         continue 

      carrier_info = CARRIERS.get(details["carrier_id"])
      # if the filters matched, we add the current load to our output list 
      out_list.append(f"{load}: {details['origin']} to {details['destination']}, Weight={details['weight_tons']} tons, Status={details['status']}, Carrier_ID={details['carrier_id']}, Carrier_name={carrier_info['name']}, Reliability={carrier_info['on_time_pct']}%, Distance={details['distance_km']} km.")
   if not out_list:
      return f"No loads found matching given filters."
   return "\n".join(out_list)  

def get_load_details(load_id:str) -> str:
   if not isinstance(load_id, str):
      return "Invalid input: load_id must be a string."
   else:
      load=LOADS.get(load_id)
      if load is None:
         return f"No load found for ID {load_id}."
      carrier_info = CARRIERS.get(load["carrier_id"])
      details = f"Load {load_id} from {load['origin']} to {load['destination']}. Weight={load['weight_tons']}, Status={load['status']}, Carrier_ID={load['carrier_id']}, Carrier_name={carrier_info['name']}, Reliability={carrier_info['on_time_pct']}%, Distance={load['distance_km']}."
      return details

def get_distance(city_a:str, city_b:str) -> str:
   if not city_a or not city_b:
      return "Invalid input. Both city names must be specified."
   if city_a.lower() == city_b.lower():
      return "Invalid input. City names cannot be the same."
   lookup_key = distance_key(city_a, city_b)
   result = DISTANCES_KM.get(lookup_key)
   if result is None:
      return f"No distance data found for the given city pair {city_a}-{city_b}."
   return f"Distance between {city_a} and {city_b} is {result}."

def sum_distances(load_ids: list) -> str:
   if not isinstance(load_ids, list):
      return "Invalid input. load_ids must be a list."
   total = 0
   for id in load_ids:
      load = LOADS.get(id)
      if load is None:
         return f"No distance for {id}."
      distance = load.get("distance_km")
      if distance == None:
         return f"No distance found for {id}."
      total += distance 
   return f"Total distance for loads {load_ids} is {total} km."
   

# ------------------- TOOL_IMPLS -------------------

TOOLS_B_IMPLS = {"list_loads": list_loads, "get_load_details": get_load_details, "get_distance": get_distance, "sum_distances": sum_distances}

# ------------------- TOOL DIRECTORY -------------------

TOOLS_B = [
   {"name": "list_loads",
    "description": "Lists details of all available loads. Optionally apply filters to search for loads by specific attributes including origin, destination, weight_tons, status, carrier_id, and distance_km. Use this before get_load_details when you don't know the load ID yet.",
    "input_schema": {
      "type": "object",
      "properties": {"origin": 
                        {"type": "string", "description": "e.g. Mumbai."}, 
                     "destination": 
                        {"type": "string", "description": "e.g. Delhi."},
                     "weight_tons": 
                        {"type": "number", "description": "unit: tons, e.g. 5."},
                     "status": 
                        {"type": "string", "description": "one of: pending, in_transit, delivered."},
                     "carrier_id": 
                        {"type": "string", "description": "e.g. CAR_01"},
                     "distance_km": 
                        {"type": "number", "description": "unit: km, e.g. 10."}
                     },
      "required": [] 
   }},
   {"name": "get_load_details",
    "description": "Fetches the details of a single load based on the load ID. Do not use to browse loads - use list_loads for that.",
    "input_schema": {
      "type": "object",
      "properties": {"load_id": {"type": "string", "description": "e.g. LOAD_001"}},
      "required": ["load_id"] 
   }},
   {"name": "get_distance",
    "description": "Fetches the distance in kilometers of a single load based on two specified cities. Order of cities does not matter.",
    "input_schema": {
      "type": "object",
      "properties": {"city_a": 
                        {"type": "string", "description": "e.g. Mumbai"}, 
                     "city_b": 
                        {"type": "string", "description": "e.g. Delhi"},
                     },
      "required": ["city_a", "city_b"] 
   }},
   {"name": "sum_distances",
    "description": "Calculates the total distance between two or more cities based on load ID. Use this instead of calling get_distance repeatedly to get a total of multiple loads.",
    "input_schema": {
      "type": "object",
      "properties": {"load_ids": {"type": "array", 
                                  "items": {"type": "string"},
                                  "minItems": 2,
                                  "description": "e.g. [LOAD_001, LOAD_002]."}},
      "required": ["load_ids"] 
   }}
]

