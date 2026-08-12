"""
The deterministic slice: functions that can be re-run to check a trace.

A guard qualifies for replay only if it is a pure function of its recorded
inputs. No clock, no randomness, no network, no filesystem, no global state.
That is the entire admission test, and it is why the flagship's claim is
"replay-faithful", not "true": we can re-derive this, so we check it, and
we say nothing at all about the steps we cannot.
"""

# posixpath, not os.path. os.path is an alias: it resolves to posixpath here
# and to ntpath on Windows, where the separator rules differ, so one recorded
# path would canonicalize two ways on two machines. The host operating system
# is global state, and the admission test above forbids it. posixpath imports
# everywhere and answers identically everywhere.
from posixpath import normpath

# The policy: where an agent is permitted to write. A tuple, not a list,
# because it is a constant and nothing should be appending to it at runtime.
ALLOWED_PREFIXES = ("workspace/", "tmp/")


def check_write_path(path: str) -> str:
    """
    Decide whether an agent may write to this path.

    Prefix matching asks a question about the characters at the front of a
    string, so the string has to be in a canonical form before the question
    means anything. "workspace/../../etc/passwd" begins with an allowed
    prefix and lands outside the agent's room; normpath collapses it to
    "../etc/passwd" before the loop ever sees it. The same pass leaves an
    honest "workspace/notes/../summary.md" as "workspace/summary.md".

    Canonicalizing rather than banning ".." is the deliberate part. The
    honest use of ".." has to keep working, and forbidding a character is a
    rule about spelling where this needs a rule about destination.

    The policy is unchanged by any of this. Only the form of its input is.

    Args:
        path: The path the agent asked to write, exactly as recorded.

    Returns:
        "allow" or "deny".
    """
    path = normpath(path)

    for prefix in ALLOWED_PREFIXES:
        if path.startswith(prefix):
            return "allow"

    # Reached only by falling out of the loop, meaning every prefix was
    # tried and none matched. The loop's exhausted case, and the line most
    # easily forgotten when this shape is written from memory.
    return "deny"
