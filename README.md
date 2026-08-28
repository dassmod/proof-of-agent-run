# Proof-of-Agent-Run

**What it is.** A replay engine for AI agent runs. It reads a recorded run and re-derives the steps a machine can re-derive.

**The question it answers.** Did this record tell the truth about the steps that can be checked?

**The question it refuses to answer.** Everything else. It says nothing about the steps it could not check, and it says so out loud.

## The three outcomes

Most verifiers have two. This one has three, and the third is the point.

| status | what it means | what it is about |
| --- | --- | --- |
| `match` | re-derived value equals the recorded one | the run |
| `divergence` | re-derived value differs from the recorded one | the run |
| `skipped` | the trace declared this step non-deterministic | the engine's reach |
| `unknown_guard` | the trace named a guard this engine does not have | the engine's reach |
| `signature_mismatch` | the engine has the guard and cannot call it | the engine's reach |

The last three are one category: **could not check.** They are facts about the engine, never about the run.

**Why that matters.** A validator that cannot separate "you lied" from "I could not look" is not a validator. It is a machine that accuses honest agents when its own reach runs out. The honest sentence is "I could not follow step 4", never "step 4 does not reproduce".

**There is no aggregate verdict, on purpose.** Collapsing a run to one pass or fail hides which steps were never checked at all. That silence is the exact thing this design refuses.

## What counts as replayable

A guard qualifies only if it is a pure function of its recorded inputs.

No clock. No randomness. No network. No filesystem. No global state.

That is the whole admission test. It is why the claim is "replay-faithful" and not "true".

**Nothing here trusts the trace.** The trace is written by the party whose honesty is in question. Every value taken from it is a claim, not a fact.

## Run it

```
python3 check.py
```

No dependencies. Standard library only. It prints one line per verdict and stops.

## The files

| file | what it is |
| --- | --- |
| `replay/guards.py` | the deterministic slice: functions that are safe to re-run |
| `replay/engine.py` | the engine, and the whitelist that maps a trace's name to a callable |
| `fixtures/runs.py` | five hardcoded traces, one job each |
| `check.py` | runs every fixture, prints what the engine said |
| `TRACE-FORMAT.md` | the trace format spec: clauses settled, clauses still open |
| `WORKLOG.md` | one dated line per work session, newest on top |

## The fixtures

| run | job |
| --- | --- |
| run-0001 | an honest record. Reports `match`. |
| run-0002 | a forgery. The recorded decision is one the guard never gave. Reports `divergence`. |
| run-0003 | a path traversal. Holds the guard to its own repair. |
| run-0004 | a renamed input key, with a forgery underneath it. Reports `signature_mismatch` and never `match`. |
| run-0005 | a recorded value of the wrong type. **Crashes the whole report.** |

**run-0005 fails on purpose.** `TRACE-FORMAT.md` states that a crash is not a verdict, and this engine does not yet meet that rule. The fixture demonstrates the gap instead of describing it. It stays until the containment lands.

## Status

Early. One guard, five fixtures, no chain yet. The spec is ahead of the engine in two places and says so.
