'''
Exercise 2.3 Break it Lab - Part 1:
This file contains the run_agent for re-benchmark.py
Do not run this file. It runs as part of re-benchmark.py

'''

from anthropic import Anthropic
import sys
import time
from dotenv import load_dotenv
load_dotenv()
#from toolset_a import TOOLS_A, TOOLS_A_IMPLS
from toolset_b import TOOLS_B, TOOLS_B_IMPLS

SYSTEM = "You are a freight data assistant. Use tools to answer; never invent data. Analyze the provided database collections exclusively using your designated tools. If a question cannot be resolved by the available tool data schemas, explicitly state that the information is unavailable. Do not reference or allow the preceding contract boilerplate text to interfere with database query parameters."

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
      self.rows = []
      self.headers = ["Iteration", "Input", "Output", "In: System", "Schemas", "History", "New"]
      self.msg_store = []
   
   def record(self, iteration, usage, old_messages, new_messages, system, tools, messages):
      input = usage.input_tokens
      output = usage.output_tokens
      in_system = estimate_tokens(str(system))
      schemas = sum(estimate_tokens(str(t)) for t in tools)
      history = sum(estimate_tokens(str(msg)) for msg in old_messages)
      new = sum(estimate_tokens(str(msg)) for msg in new_messages) 

      self.rows.append([iteration+1, input, output, in_system, schemas, history, new])
         
      startidx = len(self.msg_store)
      add_msgs = messages[startidx:]
      for msg in add_msgs:
         self.msg_store.append({"msg":str(msg), "iter": iteration+1})

      # print("\nMSG STORE: ", self.msg_store)

   def rent_of(self, message_index:int, max_iter) -> int:
      msg = self.msg_store[message_index]["msg"]
      iteration_added = self.msg_store[message_index]["iter"]
      tokens = estimate_tokens(msg)
      rent = tokens * (max_iter-iteration_added)
      return rent

   def print_ledger(self, max_iter):

      print("\n------- TOKEN LEDGER: {Question} -------")
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
      
      return total_input
         
# ------------ running the agent ------------

def run_agent(question:str, tools:list, tool_impls:dict, show) -> dict:
   client = Anthropic()
   messages = [{"role": "user", "content": question}]

   print(f"\n================= Question: {question} =================")

   iteration_count = 1
   tools_count = 0

   token_record = TokenLedger()

   for iteration in range(10): # sets the max iterations to 10 so the model doesn't run forever
      print(f"\n====================== ITERATION {iteration_count} ======================")

      msg_count = len(messages)-2
      history = messages[:msg_count]
      new = messages[msg_count:]

      response = client.messages.create(
         model="claude-sonnet-4-5",
         max_tokens=1024,
         system=SYSTEM,
         tools=tools,
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
               func = tool_impls[tool.name]
               tools_count += 1
               result = func(**tool.input)
               
               content = {"type": "tool_result", "tool_use_id": tool.id, "content": result}
               tool_results.append(content)
            except Exception as exc:
               content = {"type": "tool_result", "tool_use_id": tool.id, "content": str(exc), "is_error": True}
               tool_results.append(content)

         messages.append({"role": "user", "content": tool_results})

         token_record.record(iteration, response.usage, history, new, SYSTEM, tools, messages)

      # if this is satisfied, the model has found the final answer to give the user 
      elif response.stop_reason == "end_turn":
         if show:
            show_context(messages)
         token_record.record(iteration, response.usage, history, new, SYSTEM, tools, messages)
         final = "".join(b.text for b in response.content if b.type == "text")
         print(final)
         print("\n====================== SUMMARY ======================")
         print("Total Iterations to complete: ", iteration_count)
         print("Total tool calls requested by LLM: ", tools_count)
         total_tokens = token_record.print_ledger(iteration_count)
         print("\n======================== END ========================")
         return {"answer": final, "iterations": iteration_count, "total_tokens": total_tokens,
         "wrong_tool_calls": 3}
      
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
   run_agent(question, TOOLS_B, TOOLS_B_IMPLS, show)
   print("\n\n Time taken = ",(time.time()-start), "s")
