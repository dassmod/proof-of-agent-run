"""
The replay engine: re-derive what can be re-derived, report only what it saw.

Three outcomes exist, not two. A step can match, a step can diverge, and a
step can be one this engine is not able to check. The third is not a failure
of the run and must never be reported as one: a validator that cannot tell
"you lied" from "I do not know" is not a validator, and reporting its own
gap as the run's fault is how an honest agent gets accused.

Nothing here trusts the trace. The trace is written by the party whose
honesty is in question, so every value taken from it is treated as a claim.
"""

from replay.guards import check_write_path


# A trace names its guard with a string. The engine has to turn that string
# into something callable, and this table is the only place that happens.
# A guard absent from this table is not replayable, whatever the trace claims.
#
# This is also a whitelist, and that is the point. Looking the name up in the
# module instead (getattr) would let the trace's author choose which function
# this engine runs. Nothing outside this table is ever reachable.
GUARDS = {
    "check_write_path": check_write_path,
}


# --- one step in, one verdict out ---

def replay_step(step: dict) -> dict:
    """
    Re-derive one step and say whether the trace told the truth about it.

    Args:
        step: One step of a run, as recorded.

    Returns:
        A verdict carrying the step's index and name, a status of "skipped",
        "unknown_guard", "match" or "divergence", and for the last two the
        recorded and re-derived values so the caller can see the conflict.
    """
    # Not every step is checkable, and the trace declares which is which
    # rather than the engine guessing. A model's decision cannot be re-run,
    # and saying so out loud is the honest output, not a missing one.
    if step["kind"] != "deterministic":
        return {
            "index": step["index"],
            "name": step["name"],
            "status": "skipped",
        }

    # The engine's own gap, kept strictly apart from the run's honesty.
    if step["name"] not in GUARDS:
        return {
            "index": step["index"],
            "name": step["name"],
            "status": "unknown_guard",
        }

    guard = GUARDS[step["name"]]

    # The trace's inputs are unpacked into the guard's parameters, so the
    # format is bound to the function signature: these keys are parameter
    # names, not free-form labels. That constraint belongs in the spec.
    rederived = guard(**step["inputs"])
    recorded = step["outputs"]["decision"]

    # Plain == is enough only because guards return short strings today. The
    # moment one returns a dict or a float, this comparison needs a canonical
    # form first, or honest runs start reporting divergence.
    if rederived == recorded:
        status = "match"
    else:
        status = "divergence"

    return {
        "index": step["index"],
        "name": step["name"],
        "status": status,
        "recorded": recorded,
        "rederived": rederived,
    }


# --- one run in, one verdict per step out ---

def replay_trace(trace: dict) -> list[dict]:
    """
    Replay every step of one run.

    No aggregate verdict is returned on purpose. Collapsing a run to a single
    pass or fail would hide which steps were never checked at all, and that
    silence is exactly what this design refuses.

    Args:
        trace: One agent run, as recorded.

    Returns:
        One verdict per step, in the run's own order.
    """
    results = []

    for step in trace["steps"]:
        results.append(replay_step(step))

    return results
