# Applicability

Every plan says which design concerns it touches, and why the others don't apply.

## Rules

DA-01  Every plan declares each system-design topic (DF, DP, DS, DB, DX, DI) as `applies` or `n/a — <reason>`. A missing declaration is rejected, and an `n/a` is valid only when the plan supports its reason. The gate verifies each declaration against the plan, then evaluates every applicable rule by its own trigger.

## How

The declaration goes in the plan's `## System-design applicability` section, before `## Phases`:

```markdown
## System-design applicability
- DF: applies
- DP: n/a — no repeated fixes sharing a failed gate
- DS: applies
- DB: applies
- DX: n/a — no shared mutable state
- DI: n/a — no externally observable state changes
```

A declaration is a claim for the gate to verify, not an exemption. If a plan marks `DI: n/a — no external writes` but sends an outbound message or submits a job, the gate rejects it.

A topic-level `applies` does not switch on every rule in that topic. `DI: applies` means the plan has state-changing Actions; whether a particular Action needs a key is still decided by DI-01's trigger. Over-declaring is not a violation.

Topic keys are the rule prefixes in this book's `RULES.md`, excluding `DA`. A new topic needs a new key, and no change to the gate protocol.
