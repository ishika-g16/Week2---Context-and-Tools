"""
toolset_a.py  —  the "before" toolset. Provided, not written by you.

Study it. Feel the badness. Every choice in here is a real anti-pattern you'll
see in the wild:

  * Three vague, overlapping tools. The model can't tell which to use.
  * Descriptions that say nothing ("Query the data.").
  * Every tool dumps ENTIRE records as raw JSON — all fields, no filtering,
    no pagination. Huge tool results that then pay rent on every later step.
  * Errors are raw exceptions (stack traces) handed back to the model, which
    teach it nothing about how to recover.
  * There is NO arithmetic tool. When a question needs a sum, the model has to
    add the numbers itself — and that's where it quietly gets them wrong.

Your job in Exercise 2.2 is to design Toolset B that fixes all of this, then
prove with the benchmark that the same model on the same data does better.

NOTE on errors: these tools raise real exceptions on bad input. Your agent's
tool dispatcher should catch exceptions and pass the text back to the model as
the tool result (that is exactly the bad "stack trace as tool_result" behaviour
we want to observe). Do not "fix" these tools — measure them.
"""

import json
from freight_data import LOADS, CARRIERS, DISTANCES_KM

def query(query_string: str) -> str:
    """Query the data."""
    # Crude substring match across every load record, returns full JSON of all
    # vaguely-matching loads. No sense of fields, filters, or limits.
    q = query_string.lower()
    hits = {}
    # key=load_id, value=load
    for load_id, load in LOADS.items():
        haystack = (load_id + " " + " ".join(str(v) for v in load.values())).lower()
        if any(word in haystack for word in q.split()):
            hits[load_id] = load
    return json.dumps(hits)  # could be the entire table, dumped verbatim


def fetch_info(id: str) -> str:
    """Fetch information from the system."""
    # Overlaps with query() and get_records(). Handles loads OR carriers,
    # so the model can never be sure what it'll get back. Raw KeyError on miss.
    if id in LOADS:
        return json.dumps(LOADS[id])
    if id in CARRIERS:
        return json.dumps(CARRIERS[id])
    raise KeyError(id)  # -> stack trace handed back to the model


def get_records(record_type: str) -> str:
    """Get records."""
    # No filtering whatsoever: dumps the entire table for the requested type.
    if record_type == "loads":
        return json.dumps(LOADS)
    if record_type == "carriers":
        return json.dumps(CARRIERS)
    if record_type == "distances":
        return json.dumps(DISTANCES_KM)
    raise ValueError(f"unknown record_type: {record_type}")


# The schemas the model actually sees. Note how little they say.
TOOLS_A = [
    {
        "name": "query",
        "description": "Query the data.",
        "input_schema": {
            "type": "object",
            "properties": {"query_string": {"type": "string"}},
            "required": ["query_string"],
        },
    },
    {
        "name": "fetch_info",
        "description": "Fetch information from the system.",
        "input_schema": {
            "type": "object",
            "properties": {"id": {"type": "string"}},
            "required": ["id"],
        },
    },
    {
        "name": "get_records",
        "description": "Get records.",
        "input_schema": {
            "type": "object",
            "properties": {"record_type": {"type": "string"}},
            "required": ["record_type"],
        },
    },
]

# map names -> functions, for your agent's dispatcher
TOOLS_A_IMPLS = {"query": query, "fetch_info": fetch_info, "get_records": get_records}
