# Week 2 Starter Pack — Context & Tools

These three files are the starting point for **Exercise 2.2 (Good Tools, Bad Tools)**, and the dataset is also what you'll use for Exercise 2.1 (Token Ledger) and 2.3 (Memory & Compaction). Drop them next to your Week 1 agent.

## The files

| File | What it is | Do you edit it? |
|---|---|---|
| `freight_data.py` | The shared world: 12 loads, 5 carriers, a distance table. Both toolsets read from this same data. | **No.** Build around it. |
| `toolset_a.py` | The deliberately *bad* toolset (three vague, overlapping tools that dump raw JSON, give stack-trace errors, and have no arithmetic tool). Your benchmark "before". | **No.** Measure it, don't fix it. |
| `benchmark.py` | The 10 questions you run against both toolsets, with ground-truth answers and an objective `score_correct()` helper, plus a harness skeleton with TODOs. | Fill in the harness TODOs. |

## Your job, in order

1. **Run Toolset A first.** Wire `toolset_a.TOOLS_A` / `TOOLS_A_IMPLS` into your Week 1 agent and run all 10 benchmark questions, 3 times each. Record the four metrics in `benchmark.py` → `SCORES`: correctness, iterations, total tokens, wrong-tool calls. Expect it to struggle — that's the point.

2. **Design Toolset B on paper.** Write `toolset_b_spec.md`: for each tool, its name (verb_noun), one-line purpose, the description text the model will read, its inputs, its compact return format, and its error format. **Send this to me and we'll review it together before you write any code** — this is the real-world ritual; don't skip it.

3. **Build Toolset B** to the approved spec. Sharp single-purpose tools, minimum-necessary return fields, errors that teach recovery, and a deterministic `sum_distances(load_ids)` so the model never adds numbers itself.

4. **Run the benchmark again** against Toolset B, 3 times each, and fill in the comparison table in the Week 2 doc — explaining each row's delta in terms of *rent*, description clarity, and "the model narrates, the code decides."

## A couple of rules from the doc

- **Catch tool exceptions in your dispatcher** and pass the text back to the model as the tool result. With Toolset A that means ugly stack traces reach the model — that's the bad behaviour we want to observe and measure.
- **No arithmetic in the model.** Toolset A forces the model to add numbers itself; watch question **B3** and **B8** for wrong totals. Toolset B should make that error structurally impossible.
- **B10 is a trap.** Nothing in the data or tools can answer it. The only correct behaviour is for the agent to say it can't — not to invent a number.

## Quick check that the files load

```bash
uv run python -c "import freight_data, toolset_a, benchmark; print('starter pack OK')"
```

Questions on any of this — especially before you start designing Toolset B — just ask.
