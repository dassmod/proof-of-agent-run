"""
The deterministic slice: functions that can be re-run to check a trace.

A guard qualifies for replay only if it is a pure function of its recorded
inputs. No clock, no randomness, no network, no filesystem, no global state.
That is the entire admission test, and it is why the flagship's claim is
"replay-faithful", not "true": we can re-derive this, so we check it, and
we say nothing at all about the steps we cannot.
"""

# The policy: where an agent is permitted to write. A tuple, not a list,
# because it is a constant and nothing should be appending to it at runtime.
ALLOWED_PREFIXES = ("workspace/", "tmp/")


def check_write_path(path: str) -> str:
    """
    Decide whether an agent may write to this path.

    Prefix matching is the crudest possible way to ask "is this inside the
    agent's own room", and it has a known hole: "workspace/../../etc/passwd"
    starts with an allowed prefix. Resolving the path before checking is the
    fix, and the unresolved version makes a good second tampering fixture.

    Args:
        path: The path the agent asked to write, exactly as recorded.

    Returns:
        "allow" or "deny".
    """
    for prefix in ALLOWED_PREFIXES:
        if path.startswith(prefix):
            return "allow"

    # Reached only by falling out of the loop, meaning every prefix was
    # tried and none matched. The loop's exhausted case, and the line most
    # easily forgotten when this shape is written from memory.
    return "deny"
