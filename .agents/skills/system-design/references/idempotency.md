# Idempotency

Running it twice, or rerunning it after a crash partway through, ends in the same state.

## Rules

DI-01  Every Action that changes externally observable state is idempotent. That includes writes, job submissions, provisioning, migrations, deployments, financial entries, and outbound messages. Pure computations and side-effect-free reads are exempt.

DI-02  Every in-scope Action declares an idempotency key and a convergence check that detects whether its intended effects are already complete.

DI-03  Every in-scope Action has a crash-midway recovery test: interrupt it after a partial effect, rerun it with the same key, and verify that the externally observable outcome equals one successful run, with no unintended duplicate effects.

## How

What counts as externally observable is whether repeating the Action can produce an additional effect someone could observe. Crossing a process boundary is not the test. Durable or shared state inside one process is in scope; a pure read from an external service is not.

Derive each step from the state that exists: read the current state, compare it to the goal, and apply only the difference. A repeat run then finds nothing left to do.

Some external systems take no idempotency key. For those, establish an equivalent: a durable operation record, a transactional outbox, or reconciliation against the authoritative external id.

Account for the crash window on irreversible effects. A payment can be submitted and the process can crash before completion is recorded. A missing local acknowledgment does not mean the effect never happened, and a convergence check that reads only local rows will submit the payment twice.

Anything a run leaves behind (a lock, a temp file, a half-written record, a claimed job) must be recognizable as stale by the next run. That evidence has to hold no matter where the previous run stopped.

Idempotency does not require atomicity. Partial states may exist; recovery must converge from them without duplicating effects.
