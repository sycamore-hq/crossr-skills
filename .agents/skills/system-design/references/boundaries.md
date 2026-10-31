# Boundaries

Decide where trust changes and who owns each rule.

## Rules

DB-01  The plan identifies every trust boundary: wire protocols, files, environment variables, user input, external services, and model or agent output. Each inbound boundary has one authoritative validation and parsing path that produces trusted domain types; that path may take several steps. Interior components consume those types without repeating boundary validation.

DB-02  Every new component belongs to one architectural layer. Boundary components are thin adapters that parse inbound and serialize or perform effects outbound. Business decisions live in pure domain calculations behind them.

DB-03  Every domain invariant has exactly one authoritative owner (a type, module, or aggregate) that defines and enforces it. Other components do not reimplement its rules; constraints, assertions, and tests that derive from or delegate to the owner are allowed. New domain terms go in the glossary `code-writer` requires.

DB-04  Do not introduce a boundary, layer, or abstraction around code that is already clear and local. Every new architectural separation names the concrete responsibility or dependency that justifies it.

## How

One authoritative path is not one parsing operation. Layered or multi-step parsing is fine as long as one path is the sole producer of the trusted type.

Trust follows provenance, not process boundaries. An internal seam becomes a trust boundary only when data reaches it by bypassing the established parse path, or can be mutated outside the domain's guarantees.

Model and agent output is untrusted. Successful JSON parsing proves only syntax: not domain validity, not authorization. Checking current state just before an effect is authorization, which is a different thing from repeating boundary validation.

One authoritative owner does not mean one place that checks. Database constraints, assertions, and tests may enforce the same rule as long as they derive from or delegate to the owner. Two modules each implementing the rule their own way is the violation.

`DB-04` is the counterweight to the rest. A boundary is complexity, so it needs the same justification `subtraction.md` asks of any addition.

The function-level rules, validate at entry and make illegal states unrepresentable, live in `code-writer`.
