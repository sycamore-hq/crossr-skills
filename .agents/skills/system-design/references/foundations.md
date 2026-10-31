# Foundations

Settle what later work stands on before the work that stands on it.

## Rules

DF-01  Before implementing logic that depends on a data model, the plan settles that model: domain types, schemas, wire shapes, and state ownership. Dependent logic never precedes the model it relies on. Settled means validated enough for the dependent work, not frozen.

DF-02  The plan schedules first the foundational work that enables or de-risks later phases in the same plan, and each foundational phase names the phases it enables. Work justified only by hypothetical future needs is not foundational. When two phases are both ready, the one that enables downstream work goes first. This is a dependency order, not a global barrier: independent work may run concurrently.

## How

Order is subtract → foundation → dependent work. That is a dependency order, not three global barriers: independent work runs concurrently, and dependent work never outruns its prerequisites. This is the one place that order is stated; `subtraction.md` points here.

"Settled" means defined and validated enough for the dependent phase, not frozen. A schema spike or a fixture that informs the model is fine. Substantial business logic written against an unresolved contract is not.

Data shape comes first because a late change to it is a rewrite and an early one is a one-line diff. Trace every access pattern and pick shapes that fit the dominant paths.

Scaffold is foundational only when this plan's later phases use it. A test harness four later phases depend on qualifies. A plugin framework for features that might come does not.

The function-level rule, data shape before logic, lives in `code-writer`.
