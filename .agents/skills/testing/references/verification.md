## Verification

In a fresh activation the following behaviors are directly observable and scorable:

- The agent applies the coverage, Arrange-Act-Assert, error-path, and isolation requirements of this card and, when one exists, the rules tagged `test` in the disclosed book's Rules projection item-by-item to the proposed changes or existing code, explicitly naming each violation found (e.g., "coverage: `calculate_total` public function has no unit tests", "violates RT-04: error path `Err(InvalidInput)` in `parse_config` untested").
- The agent maps each claimed AC id to at least one test (naming the test) and reports any previously passing test that now fails as a REJECT blocker.
- The agent verifies the test situation against the disclosed book Rules projection when one exists (pure calculations must be trivially testable; actions isolated) and flags any gaps in testability or coverage.
- The agent requires that all violations be resolved via minimal, exact delegation to the writer layer (no unrelated refactors or "while you're here" changes) and re-evaluates the result until it would pass a fresh review under this skill.
- The agent emits its verdict per the `gan-verdict` contract; the output structure and language itself exemplify clear, intention-revealing, high-signal pedantry with zero fluff.

Violations against any of these observable criteria during fresh activation indicate the skill was not followed and must be corrected before the work can be considered complete.
