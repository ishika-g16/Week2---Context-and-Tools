from anthropic import Anthropic
import sys
import time
from dotenv import load_dotenv
load_dotenv()
from toolset_b import TOOLS_B, TOOLS_B_IMPLS


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
   
   def record(self, iteration, usage, old_messages, new_messages, system, tools, messages):
      input = usage.input_tokens # ground truth 
      output = usage.output_tokens # ground truth 
      in_system = estimate_tokens(str(system)) # system prompt 
      schemas = sum(estimate_tokens(str(t)) for t in tools) # tool schema 
      history = sum(estimate_tokens(str(msg)) for msg in old_messages) # all earlier messages 
      new = sum(estimate_tokens(str(msg)) for msg in new_messages) # newer messages being sent to the LLM for the first time

      self.rows.append([iteration+1, input, output, in_system, schemas, history, new])
         
      startidx = len(self.msg_store) 
      add_msgs = messages[startidx:]
      for msg in add_msgs:
         self.msg_store.append({"msg":str(msg), "iter": iteration+1}) # messages stored in text, iteration pairs 
      # print("\nMSG STORE: ", self.msg_store)

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

# ------------ managing memory with compaction ------------

def compact(messages: list, keep_recent: int = 2) -> list:
   # todo: summarize all but the last keep_recent messages into ONE
   # assistant message. CRITICAL: the summarization prompt must demand
   # that IDs and numbers survive verbatim ("LOAD_017, 11T, Chennai→Delhi").
   # Generic summaries lose exactly the facts agents need.
   if(len(messages)<4):
      return messages

   end_idx = len(messages) - keep_recent
   sum_messages = str(messages[1:end_idx])
   keep_messages = messages[-keep_recent:]

   head = messages[0]

   client = Anthropic()
   summary = client.messages.create(
      model="claude-sonnet-4-6",
      max_tokens=1024,
      system="You are a conversation summarizer for a freight agent. You MUST extract and PRESERVE all specific important data values VERBATIM (load IDs (e.g. LOAD_001), weights (e.g. 11t), city names (e.g. Chennai→Delhi), distances (e.g. 1420km), statuses (e.g. in_transit)) from the conversation. Return a concise, factual summary.",
      messages=[{"role": "user", "content": sum_messages}]
   )

   final_message = {"role": "user", "content": f"SUMMARY: {summary.content[0].text}."}

   final = [head] + [final_message] + keep_messages
   print("================= MESSAGE COMPACTED =================\n")
   return final
         
# ------------ running the agent ------------

def run_agent(question:str, show:bool=False) -> str:
   client = Anthropic()
   messages = [{"role": "user", "content": question}]

   iteration_count = 1
   tools_count = 0
   compact_limit = 4

   token_record = TokenLedger()

   for iteration in range(10): # sets the max iterations to 10 so the model doesn't run forever
      print(f"\n====================== ITERATION {iteration_count} ======================")

      # compaction 
      if len(messages)>compact_limit:
         messages = compact(messages)
      
      msg_count = len(messages)-2
      history = messages[:msg_count]
      new = messages[msg_count:]
      
      # print(f"HISTORY FOR THIS ITERATION IS: {history}")
      # print(f"\n\nNEW MESSAGES: {new}\n\n")

      response = client.messages.create(
         model="claude-sonnet-4-6",
         max_tokens=1024,
         system=SYSTEM,
         tools=TOOLS_B,
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
               func = TOOLS_B_IMPLS[tool.name]
               tools_count += 1
               result = func(**tool.input)
               
               content = {"type": "tool_result", "tool_use_id": tool.id, "content": result}
               tool_results.append(content)
            except Exception as exc:
               content = {"type": "tool_result", "tool_use_id": tool.id, "content": str(exc), "is_error": True}
               tool_results.append(content)

         messages.append({"role": "user", "content": tool_results})

         token_record.record(iteration, response.usage, history, new, SYSTEM, TOOLS_B, messages)

      # if this is satisfied, the model has found the final answer to give the user 
      elif response.stop_reason == "end_turn":
         if show:
            show_context(messages)
         token_record.record(iteration, response.usage, history, new, SYSTEM, TOOLS_B, messages)
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
