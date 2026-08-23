"""
Hardcoded agent-run traces. Four runs, one shape, four different jobs.

HONEST_RUN records what a correct guard actually said, so replay reports a
match. TAMPERED_RUN records a decision the guard never gave, so replay
reports a divergence, and that is the forgery case. TRAVERSAL_RUN records a
path that begins inside the agent's room and lands outside it: it holds the
guard to its repair, reporting a match today and a divergence the day the
path stops being canonicalized. RENAMED_INPUT_RUN records its argument
under a key the guard has no parameter for, so the engine cannot call the
guard at all and reports signature_mismatch.

That fourth run carries a forgery underneath the mismatch, on purpose: its
recorded decision is a lie the guard would have caught. The report still
says signature_mismatch, and never says match, which is the distinction the
whole design rests on. A step the engine could not check is not a step that
passed, and a clean-looking report over an unreplayable step is worth
nothing.

Every step carries `kind`, and that field is the whole design. A run is not
verifiable or unverifiable as a unit: it is a sequence in which some steps
can be re-derived and some cannot, and the format has to say which is which
before any engine can act. Splitting the run is the contribution; replaying
the deterministic part is the easy half.

`kind` is also written by the party under suspicion, and nothing here stops
an agent from marking every step nondeterministic, replaying perfectly
clean, and having said nothing at all. The trace-format spec has to answer
that or state plainly that it does not.

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
            "outputs": {
                "tool": "write_file",
                "path": "workspace/summary.md",
            },
        },
        {
            "index": 1,
            "kind": "deterministic",
            "name": "check_write_path",
            # These keys are the guard's parameter names, not free-form
            # labels. The engine calls the guard with **inputs, so the
            # trace format is bound to the function signature. That
            # constraint goes in the spec.
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
            "outputs": {
                "tool": "write_file",
                "path": "/etc/passwd",
            },
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


TRAVERSAL_RUN = {
    "run_id": "run-0003",
    "steps": [
        {
            "index": 0,
            "kind": "nondeterministic",
            "name": "model_decision",
            "inputs": {"prompt": "save the summary"},
            "outputs": {
                "tool": "write_file",
                "path": "workspace/../../etc/passwd",
            },
        },
        {
            "index": 1,
            "kind": "deterministic",
            "name": "check_write_path",
            "inputs": {"path": "workspace/../../etc/passwd"},
            # A regression test, not a forgery. This path begins with an
            # allowed prefix and lands outside the agent's room, which is
            # exactly the case the guard missed before it canonicalized
            # its input. The recorded answer is what a correct guard
            # gives, so this run reports match for as long as the guard
            # stays correct, and reports divergence the day somebody
            # removes the normalization.
            #
            # It was written the other way round on purpose, recording
            # "allow" so the pre-fix guard would agree with it, and it was
            # run once in that state. A fixture that demonstrates a broken
            # guard cannot outlive the repair: it either converts into an
            # alarm like this one, or it is deleted.
            "outputs": {"decision": "deny"},
        },
    ],
}


RENAMED_INPUT_RUN = {
    "run_id": "run-0004",
    "steps": [
        {
            "index": 0,
            "kind": "nondeterministic",
            "name": "model_decision",
            "inputs": {"prompt": "save the summary"},
            "outputs": {
                "tool": "write_file",
                "path": "/etc/passwd",
            },
        },
        {
            "index": 1,
            "kind": "deterministic",
            "name": "check_write_path",
            # "target", not "path". The guard's parameter is named path, so
            # this dict cannot be unpacked into it: the call dies at the
            # door and the guard's body never runs. Three causes produce
            # this one signal and the engine cannot tell them apart. The
            # trace was forged, the guard was refactored, or an honest
            # rename drifted the two documents apart. So the verdict says
            # only what the engine knows, which is that it could not
            # follow this step.
            "inputs": {"target": "/etc/passwd"},
            # Never read. The engine returns from the mismatch branch
            # before it reaches this field, and recording a lie here is the
            # whole point: the guard would answer "deny" for this path, so
            # this run is a forgery the report does not expose and cannot.
            # signature_mismatch is not a pass, and this fixture exists to
            # make reading it as one impossible.
            "outputs": {"decision": "allow"},
        },
    ],
}
