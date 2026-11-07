# Specialization

Precondition: the work is an architectural decision or plan, with `plan-writer` active at plan time or `code-writer` active outside the plan loop.

This book supplies the plan-level design discipline: dependency order, premise attack, subtraction, trust boundaries, invariant ownership, shared-state authority, and idempotent effects. It does not restate `code-writer`'s function-level rules, its Data / Calculations / Actions split, or its Fines.

It is a cross-cutting book (`metadata.scope: "cross-cutting"`). The harness discloses it alongside whichever language book the PBI selects, and never in place of one. It names no language. Language books supply the idioms that realize its rules.

Postcondition: combined output satisfies the active card (`plan-writer` or `code-writer`) + the language book + this book with zero contradictions.
