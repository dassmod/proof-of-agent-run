"""
Run every fixture through the replay engine and print one line per verdict.

This is the PRIMM Run stage made cheap. The engine's whole value is that its
answer arrives in under a second, so nothing here filters or judges. It
prints what the engine said, in the engine's own order, and stops.
"""

from fixtures.runs import (
    HONEST_RUN,
    RENAMED_INPUT_RUN,
    TAMPERED_RUN,
    TRAVERSAL_RUN,
    BAD_TYPE_RUN
)
from replay.engine import replay_trace


RUNS = (HONEST_RUN, TAMPERED_RUN, TRAVERSAL_RUN, RENAMED_INPUT_RUN, BAD_TYPE_RUN)


for trace in RUNS:
    print(trace["run_id"])

    for verdict in replay_trace(trace):
        # recorded and rederived exist only on match and divergence. On a
        # skipped or unknown_guard verdict their absence is the correct
        # state, not a missing field, so they are asked for rather than
        # indexed.
        detail = ""
        if "recorded" in verdict:
            detail = (
                f"  recorded={verdict['recorded']}"
                f" rederived={verdict['rederived']}"
            )

        line = (
            f"  {verdict['index']}  "
            f"{verdict['name']:<20} "
            f"{verdict['status']}{detail}"
        )
        print(line)

    print()