"""
Hardcoded agent-run traces. Two runs, identical in shape, one of them lying.

Every step carries `kind`, and that field is the whole design. A run is not
verifiable or unverifiable as a unit: it is a sequence in which some steps
can be re-derived and some cannot, and the format has to say which is which
before any engine can act. Splitting the run is the contribution; replaying
the deterministic part is the easy half.

Two separate things disqualify a step from replay, and the format does not
yet distinguish them. A model decision is out because it is unpredictable.
A write is out because it changes the world, so replaying it would perform
the action again. Both are "nondeterministic" here, which the trace-format
spec will have to either justify or split.
"""

HONEST_RUN = {
    "run_id": "run-0001",
    "steps": [
        {
            "index": 0,
            "kind": "nondeterministic",
            "name": "model_decision",
            "inputs": {"prompt": "save the summary"},
            "outputs": {"tool": "write_file", "path": "workspace/summary.md"},
        },
        {
            "index": 1,
            "kind": "deterministic",
            "name": "check_write_path",
            # These keys are the guard's parameter names, not free-form labels.
            # The engine calls the guard with **inputs, so the trace format is
            # bound to the function signature. That constraint goes in the spec.
            "inputs": {"path": "workspace/summary.md"},
            "outputs": {"decision": "allow"},
        },
    ],
}


TAMPERED_RUN = {
    "run_id": "run-0002",
    "steps": [
        {
            "index": 0,
            "kind": "nondeterministic",
            "name": "model_decision",
            "inputs": {"prompt": "save the summary"},
            "outputs": {"tool": "write_file", "path": "/etc/passwd"},
        },
        {
            "index": 1,
            "kind": "deterministic",
            "name": "check_write_path",
            "inputs": {"path": "/etc/passwd"},
            # The lie, and the only difference from an honest run. Nothing
            # here is malformed; no schema check would catch it. The guard,
            # given this path, returns "deny".
            "outputs": {"decision": "allow"},
        },
    ],
}
