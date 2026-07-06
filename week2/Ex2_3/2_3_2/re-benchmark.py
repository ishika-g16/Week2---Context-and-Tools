'''
Exercise 2.3 Break it Lab - Part 1:
Added irrelevant info to the system prompt.
SYSTEM = "You are a freight data assistant. Use tools to answer; never invent data. Analyze the provided database collections exclusively using your designated tools. If a question cannot be resolved by the available tool data schemas, explicitly state that the information is unavailable. Do not reference or allow the preceding contract boilerplate text to interfere with database query parameters."
This file calls run_agent from breakit_1.py 

'''

import sys 

BENCHMARK = [
    {
        "id": "B1", "category": "single_lookup",
        "question": "What's the status of LOAD_007?",
        "accept": ["pending"],
    },
    {
        "id": "B2", "category": "aggregate",
        "question": "Which carrier runs the most Delhi-bound loads, and how many?",
        # Delhi-bound = LOAD_001, 003, 009, 010, 011 -> CAR_01 has 2 (001, 009)
        "accept": ["CAR_01", "Sharma Logistics"],
    },
    {
        "id": "B3", "category": "arithmetic",
        "question": "What is the total distance of all pending loads, in km?",
        # pending = 001(1420)+003(2180)+005(1500)+007(980)+009(1580)+011(1420)
        "accept": ["9080", "9,080"],
        "must_not_say": [],
    },
    {
        "id": "B4", "category": "lookup_distance",
        "question": "How far is LOAD_001's trip?",
        "accept": ["1420", "1,420"],
    },
    {
        "id": "B5", "category": "filter",
        "question": "List all loads currently in transit.",
        # in_transit = 002, 006, 010
        "accept_all": ["LOAD_002", "LOAD_006", "LOAD_010"],
    },
    {
        "id": "B6", "category": "comparison",
        "question": "Which pending load is the heaviest, and how heavy is it?",
        # pending weights: 001=8,003=11,005=9,007=12,009=15,011=13 -> 009 @ 15T
        "accept_all": ["LOAD_009", "15"],
    },
    {
        "id": "B7", "category": "filter_count",
        "question": "How many loads weigh more than 10 tons?",
        # >10: 002(14),003(11),007(12),009(15),011(13) -> 5  (010 is exactly 10)
        "accept": ["5"],
        "must_not_say": ["6"],
    },
    {
        "id": "B8", "category": "arithmetic",
        "question": "What is the combined distance of LOAD_001 and LOAD_003?",
        # 1420 + 2180 = 3600
        "accept": ["3600", "3,600"],
    },
    {
        "id": "B9", "category": "lookup_attribute",
        "question": "Which carrier has the best on-time reliability?",
        # CAR_03 Reliable Freight @ 96%
        "accept": ["CAR_03", "Reliable Freight"],
    },
    {
        "id": "B10", "category": "trap_unanswerable",
        "question": "What is the estimated driving time in hours for LOAD_005?",
        # No speed/time data or tool exists. Correct = admit it can't be computed.
        "accept": ["cannot", "can't", "no", "not able", "don't have", "unable",
                   "no information", "not available", "unfortunately", "unavailable"],
        "must_not_say": [],
    },
]

# The four metrics you record per question, per toolset (averaged over 3 runs):
SCORES = [
    "correct",            # did the final answer contain an accepted value?
    "iterations",         # how many model calls the loop took
    "total_tokens",       # sum of input+output tokens across the run
    "wrong_tool_calls",   # tools called whose result didn't contribute
]


def score_correct(answer_text: str, case: dict) -> bool:
    """Objective correctness check for one answer against one case."""
    text = answer_text.lower()
    for bad in case.get("must_not_say", []):
        if bad.lower() in text:
            return False
    if "accept_all" in case:
        return all(s.lower() in text for s in case["accept_all"])
    return any(s.lower() in text for s in case["accept"])


# ---------------------------------------------------------------------------
# Harness skeleton. `run_agent` is YOUR Week 1 agent, adapted to take a toolset
# and return both the final text and the run's trace/metrics. Fill in the TODOs.
# ---------------------------------------------------------------------------
def run_benchmark(run_agent, tools, tool_impls, show, runs: int = 3):
    """
    run_agent(question, tools, tool_impls) should return a dict like:
        {"answer": str, "iterations": int, "total_tokens": int,
         "wrong_tool_calls": int}
    """
    results = []
    for case in BENCHMARK:
        per_run = []
        total_correct = 0
        for _ in range(runs):
            out = run_agent(case["question"], tools, tool_impls, show)
            per_run.append({
                "correct": score_correct(out["answer"], case), # bool
                "iterations": out["iterations"],
                "total_tokens": out["total_tokens"],
                "wrong_tool_calls": out["wrong_tool_calls"]
                })
            ...
        total_runs = len(per_run)
        for run in per_run: 
            if run["correct"]: 
                total_correct += 1
        avg_iters = sum(run["iterations"] for run in per_run) / total_runs
        avg_tokens = sum(run["total_tokens"] for run in per_run) / total_runs
        avg_wrong_tools = sum(run["wrong_tool_calls"] for run in per_run) / total_runs
        results.append({
            "id": case["id"], 
            "category": case["category"],
            "correct": total_correct, 
            "iters": avg_iters, 
            "tokens": avg_tokens, 
            "wrong-tool": avg_wrong_tools
        })
    # todo: print a table: id | category | correct | iters | tokens | wrong-tool
    headers = ["id", "category", "correct", "iters", "tokens", "wrong-tool"]
    print("Total Runs = ", total_runs)
    for col in headers:
        print(col.ljust(20), end="")
    print()
    for row in results:
        for key, value in row.items():
            print(str(value).ljust(20), end="")
        print()

    return results


if __name__ == "__main__":
   #from toolset_b import TOOLS_B, TOOLS_B_IMPLS
   from breakit_1 import run_agent
   show = "--show-context" in sys.argv
   #run_benchmark(run_agent, TOOLS_B, TOOLS_B_IMPLS, show)

   from toolset_a import TOOLS_B, TOOLS_B_IMPLS
   #from loop_W2_toolA import run_agent
   run_benchmark(run_agent, TOOLS_B, TOOLS_B_IMPLS, show)