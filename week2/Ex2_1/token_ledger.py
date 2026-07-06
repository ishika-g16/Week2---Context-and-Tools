from anthropic import Anthropic
import sys
import time
from dotenv import load_dotenv
load_dotenv()

# ------------ the world (deterministic, in-memory) ------------

LOADS = {
   "LOAD_001": {"origin": "Mumbai", "destination": "Delhi", "weight_tons": 8, "status": "pending"},
   "LOAD_002": {"origin": "Pune", "destination": "Bangalore", "weight_tons": 14, "status": "in_transit"},
   "LOAD_003": {"origin": "Chennai", "destination": "Delhi", "weight_tons": 11, "status": "pending"},
   "LOAD_004": {"origin": "Delhi", "destination": "Hyderabad", "weight_tons": 12, "status": "completed"}
}
DISTANCES_KM = {("Mumbai", "Delhi"): 1420, ("Pune", "Bangalore"): 840, ("Chennai", "Delhi"): 2180, ("Delhi", "Hyderabad"): 3020}

# ------------ tools ------------

# lists all the loads available in our database, by load id, origin, and destination 
def list_loads() -> str:
   load_string = ""
   for i in LOADS:
      load_string += f"\n{i} from {LOADS[i]['origin']} to {LOADS[i]['destination']}."
   return load_string

# for a specific load id, displays all details including origin, destination, weight, and status 
def get_load(load_id:str) -> str:
   load = LOADS.get(load_id)
   if load is None:
      return f"No load found with load id {load_id}. "
   load_data = f"Load ID: {load_id}, Origin: {load['origin']}, Destination: {load['destination']}, Weight: {load['weight_tons']}, Status: {load['status']}."
   return load_data

# fetches the distance based on the given origin and destination
def compute_distance(origin:str, destination:str) -> str:
   dist = DISTANCES_KM.get((origin, destination)) or DISTANCES_KM.get((destination, origin))
   if dist is None:
      return f"No distance data found for given origin {origin} and destination {destination}."
   return f"Distance from {origin} to {destination} is {dist} kilometers."
   

TOOLS_impls = {"list_loads": list_loads, "get_load": get_load, "compute_distance": compute_distance}

TOOLS = [
   {"name": "list_loads",
    "description": "Shows the details of all available loads, including load ID and lanes for each load.",
    "input_schema": {
      "type": "object",
      "properties": {},
      "required": []
   }},
   {"name": "get_load",
   "description": "Looks up details (origin, destination, weight in tons, and status) for one freight by its load ID. Do not call this when the user only asks for distances.",
   "input_schema": {
      "type": "object",
      "properties": {"load_id": {"type": "string", "description": "e.g. LOAD_001"}},
      "required": ["load_id"]
   }},
   {"name": "compute_distance",
   "description": "Using the given origin and destination strings, it looks up the distance in kilometers from the table.",
   "input_schema": {
      "type": "object",
      "properties": {"origin": {"type": "string", "description": "e.g. Mumbai"}, "destination": {"type": "string", "description": "e.g. Delhi"}},
      "required": ["origin", "destination"]
   }}
]

SYSTEM = "You are a freight data assistant. Use tools to answer; never invent data."

def show_context(messages:list) -> None:
   count = 1
   for item in messages:
      print(f"{count} - Role: {item['role']}, Content: {item['content']}\n")
      count += 1

# ------------ token-use and cost add ons ------------

def estimate_tokens(text:str) -> int:
   # estimating that 1 token is approx 4 characters 
   return max(1, len(text) // 4)

class TokenLedger:
   def __init__(self):
      self.rows = [] # 1 row = 1 iteration
      self.headers = ["Iteration", "Input", "Output", "In: System", "Schemas", "History", "New"]
      self.msg_store = [] # storing all messages to get the rent 
   
   # this is called every iteration to keep a track of the token count with each call
   def record(self, iteration, usage, old_messages, new_messages, system, tools, messages):
      input = usage.input_tokens # ground truth 
      output = usage.output_tokens # ground truth 
      in_system = estimate_tokens(str(system)) # system prompt 
      schemas = sum(estimate_tokens(str(t)) for t in tools) # tool schema 
      history = sum(estimate_tokens(str(msg)) for msg in old_messages) # all earlier messages 
      new = sum(estimate_tokens(str(msg)) for msg in new_messages) # newer messages being sent to the LLM for the first time

      self.rows.append([iteration+1, input, output, in_system, schemas, history, new])
         
      # only appending the newer messages that were added to the list 
      startidx = len(self.msg_store) 
      add_msgs = messages[startidx:]
      for msg in add_msgs:
         self.msg_store.append({"msg":str(msg), "iter": iteration+1}) # messages stored in text, iteration pairs 
      # print("\nMSG STORE: ", self.msg_store)

   # calculates the rent of a single message
   def rent_of(self, message_index:int, max_iter) -> int:
      msg = self.msg_store[message_index]["msg"] 
      iteration_added = self.msg_store[message_index]["iter"]
      tokens = estimate_tokens(msg)
      rent = tokens * (max_iter-iteration_added)
      return rent

   def print_ledger(self, max_iter, question):
      print(f"\n------- TOKEN LEDGER: {question} -------")
      # printing per-iteration table
      for col in self.headers:
         print(col.ljust(15), end="")
      print()
      for row in self.rows:
         for col in row:
            print(str(col).ljust(15), end="")
         print()

      # calculating cumulative totals 
      total_input = sum(row[1] for row in self.rows)
      total_output = sum(row[2] for row in self.rows)
      print(f"Total Input Tokens: {total_input}")
      print(f"Total Output Tokens: {total_output}\n")

      print("------- TOP 3 RENT PAYERS -------\n")
      #calculating the top 3 rent payers 
      total_rent = []
      for i, msg in enumerate(self.msg_store):
         total_rent.append({"msg": msg, "rent":self.rent_of(i, max_iter)})
      top3 = sorted(total_rent, key= lambda x: x["rent"], reverse=True)[:3]
      
      for item in top3:
         msg = item["msg"]
         rent = item["rent"]
         print(f"Message: {msg} with rent = {rent}\n")
         
# ------------ running the agent ------------

def run_agent(question:str, show:bool=False) -> str:
   client = Anthropic()
   messages = [{"role": "user", "content": question}]

   iteration_count = 1
   tools_count = 0

   token_record = TokenLedger()

   for iteration in range(10): # sets the max iterations to 10 so the model doesn't run forever
      print(f"\n====================== ITERATION {iteration_count} ======================")

      msg_count = len(messages)-2
      history = messages[:msg_count]
      new = messages[msg_count:]
      
      # print(f"HISTORY FOR THIS ITERATION IS: {history}")
      # print(f"\n\nNEW MESSAGES: {new}\n\n")

      response = client.messages.create(
         model="claude-sonnet-4-6",
         max_tokens=1024,
         system=SYSTEM,
         tools=TOOLS,
         messages=messages
      )

      if response.stop_reason == "tool_use":
         messages.append({"role": "assistant", "content": response.content})

         # get the entire tool use block and set the result by calling the function
         tool_reqs = [b for b in response.content if (b.type == "tool_use")]
         tool_results = []

         # run through the list of tool requests given by the model
         for tool in tool_reqs:
            try: 
               func = TOOLS_impls[tool.name]
               tools_count += 1
               result = func(**tool.input)
               
               content = {"type": "tool_result", "tool_use_id": tool.id, "content": result}
               tool_results.append(content)
            except Exception as exc:
               content = {"type": "tool_result", "tool_use_id": tool.id, "content": str(exc), "is_error": True}
               tool_results.append(content)

         messages.append({"role": "user", "content": tool_results})

         token_record.record(iteration, response.usage, history, new, SYSTEM, TOOLS, messages)

      # if this is satisfied, the model has found the final answer to give the user 
      elif response.stop_reason == "end_turn":
         if show:
            show_context(messages)
         token_record.record(iteration, response.usage, history, new, SYSTEM, TOOLS, messages)
         final = "".join(b.text for b in response.content if b.type == "text")
         print(final)
         print("\n====================== SUMMARY ======================")
         print("Total Iterations to complete: ", iteration_count)
         print("Total tool calls requested by LLM: ", tools_count)
         token_record.print_ledger(iteration_count, question)
         print("\n======================== END ========================")
         return
      
      else:
         raise RuntimeError(f"Unhandled stop_reason: {response.stop_reason}")
      
      iteration_count += 1

      if show:
         show_context(messages)
   
   return "ERROR: hit iteration ceiling — agent may be looping."

# ------------ Main ------------

if __name__ == "__main__":
   start = time.time()
   show = "--show-context" in sys.argv # true if --show-context was in sys.argv
   question = next(a for a in sys.argv[1:] if not a.startswith("--"))
   run_agent(question, show=show)
   print("\n\n Time taken = ",(time.time()-start), "s")
