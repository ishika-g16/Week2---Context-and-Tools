# Designing better tools

## Available Data

* LOADS
* DISTANCES_KM and distance_key (Helper function for distances)
* CARRIERS  

## New tools 

1. list_loads(origin=None, destination=None, weight_tons=None,  status=None, carrier_id=None, distance_km=None) -> str
  * From the LOADS table, list all the available loads and their details if no arguments are specified
  * We can pass arguments to filter by specific attributes 
2. get_load_details(load_id:str) -> str
  * By default, looks up the LOADS table using a specific load id
  * Show all details of that load
3. get_distance(city_a:str, city_b:str) -> str
  * Uses the helper function to format the input
  * Looks up the distance requested from the DISTANCES_KM table
4. sum_distances(*load_ids) -> str
  * for each load id, it will fetch the distance from the LOADS table 
  * then, it will add all of these and return the sum 
