# Verification

In a fresh activation the following behaviors are directly observable and scorable:

- The agent recites the system-design book's One-Sentence Mandate before planning.
- The plan carries a `## System-design applicability` section that declares every topic, with a reason for each `n/a`.
- The agent loads only the references whose situation matches the decision, and never feeds How to an adversary.
- Applicable obligations become claims that prove them (a subtraction list, a data model, a census, a crash test), not claims that restate the rule.
- The plan orders work subtract → foundation → dependent, and dependent work never precedes its prerequisites.

## Gate interpretation

| Condition | Verdict |
|---|---|
| Every topic declared, each `n/a` reason supported by the plan | BLESS |
| Topic omitted, or `n/a` despite evidence its trigger applies | REJECT |
| Topic marked `applies` but no rule triggers, no violation | BLESS |
| Subtraction pass explicit (removals listed, or empty with a reason) | BLESS |
| Subtraction pass omitted, or added complexity left unjustified | REJECT |
| Removal and replacement atomic for safety, removal verified separately | BLESS |
| Dependent logic starts against an unresolved data model | REJECT |
| Foundation justified only by hypothetical future work | REJECT |
| External input, including model output, reaches domain logic unparsed | REJECT |
| Two modules independently implement the same invariant | REJECT |
| Business decisions embedded in a transport adapter | REJECT |
| New abstraction with no concrete responsibility | REJECT |
| Shared mutable state guarded by convention or an advisory lock | REJECT |
| In-scope Action with no key, convergence check, or crash-midway test | REJECT |
| Third fix attempted on a premise after two failures on the same gate | REJECT |

Violations against any of these during fresh activation mean the book was not followed.
