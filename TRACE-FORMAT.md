# The trace format

What a recorded agent run must contain for this engine to replay it, and
what the engine promises back. Written after rung 1 rather than before it,
on purpose: every clause here is something the code needed, so the format
is evidence rather than a guess.

The framing this document exists to protect: replaying a trace proves
**replay-faithfulness of a self-reported trace**. It never proves that an
agent run was correct, honest, or safe. A trace is written by the party
whose honesty is in question, so every field in it is a claim.

## Status of this document

Settled: clause 1, clause 3.
Open, and named so the gap is visible: clause 2, clause 5.

---

## Clause 1 · `inputs` keys are the guard's parameter names

A recorded step names its guard with a string and carries its arguments as
a dict. The engine calls `guard(**step["inputs"])`, so the keys of that
dict are not labels. They are the parameter names of the function that will
re-derive the step.

**The trade, stated out loud because the format chose one side of it.**
Executable keys are checked by the language at the moment of the call, so a
trace that does not fit its guard cannot quietly produce a verdict. The
cost is that the format is welded to a function signature: rename `path` to
`target` in `guards.py` in six months, and every trace ever recorded stops
replaying, everywhere, permanently. Free-form labels would survive any
refactor and would not be callable, so something would have to translate
them, and that translator is one more place a wrong binding can happen
silently.

The format chose executable over stable. A guard's parameter names are
therefore public interface, and renaming one is a breaking change to the
format itself, not a local edit.

## Clause 2 · `kind` is declared per step, and that is a hole

Each step declares `kind`, and the engine does not infer it. Today only
`"deterministic"` steps are replayed.

**Open.** `kind` is written by the party under suspicion. An agent that
marks every step non-deterministic replays perfectly clean and has said
nothing at all. Two candidate answers are recorded in `fixtures/runs.py`:
bind `kind` to membership in `GUARDS` so the trace stops getting a vote, or
report coverage so a fully skipped run cannot read as a clean one. Until
one is chosen, a clean replay of a mostly-skipped trace means very little,
and this document says so rather than letting the silence flatter the run.

## Clause 3 · Three outcomes, and the third is not a failure of the run

A step can **match**, a step can **diverge**, and a step can be one this
engine **could not check**. The third is a fact about the engine, never
about the run, and reporting it as divergence is how an honest agent gets
accused of forgery by a validator that was simply unable to look.

**The two vocabularies, kept apart.** `allow` and `deny` are the guard's
words: verdicts about the agent's action, and only a guard that actually
ran can say them. `match`, `divergence` and the could-not-check family are
the engine's words: verdicts about the recording. Writing `deny` where the
engine means "I could not check" puts one layer's word in the other layer's
place, and the resulting report describes the observer's gap as the world's
fault.

The honest sentence for the third outcome is **"I could not follow step
4"**, not "step 4 does not reproduce". One letter of difference, and it is
the whole clause: the first describes the validator, the second accuses the
notebook.

**Could-not-check is a category, not a single status.** Three causes reach
it, and the report keeps them distinct, because collapsing them into one
word destroys the only signal clause 2 has to work with:

- `skipped` — the trace declared the step non-deterministic. The boundary
  was drawn by the trace's author.
- `unknown_guard` — the trace claimed a replayable step and named a guard
  this engine does not have. The engine's own gap.
- `signature_mismatch` — the engine has the guard and cannot call it: the
  recorded `inputs` keys do not fit the guard's parameters.

**Why `signature_mismatch` accuses nobody.** Three causes produce the same
signal, and from where the engine sits they are indistinguishable: the
trace was forged, the guard was refactored, or an honest rename drifted the
two documents apart. The engine cannot arbitrate between them. The only
sentence it can write truthfully is about itself.

**A crash is not a verdict.** An unrunnable step must return a verdict, not
raise. An uncaught exception ends the replay of the whole run, so one step
the engine cannot check erases the report for every step it could have.
The engine's failure to speak about one step must not become a failure to
speak about the others.

**And the fix must not swallow more than it means to.** Wrapping the guard
call in `try/except TypeError` would also catch a `TypeError` raised inside
a guard's body, which is a real bug in this repo's own code, and would
relabel that bug as "I could not check". That is the same conflation as
writing `deny`, one layer over: a defect in the engine wearing the
vocabulary of a limit of the engine. The check belongs at the door, before
the body runs.

## Clause 4 · No aggregate verdict

`replay_trace` returns one verdict per step, in the run's own order, and
never a single pass or fail for the run. Collapsing a run to one word hides
which steps were never checked at all, and that silence is what this design
refuses.

## Clause 5 · What counts as equal

**Open.** Comparison is currently plain `==` on the recorded and re-derived
values, which is the strictest possible policy, arrived at by nobody
choosing it. It survives only while guards return short strings. The moment
a guard returns a float, a dict, or anything with an ordering that is not
guaranteed, honest runs begin reporting divergence, and the format has to
say which differences count and which do not before that happens.
