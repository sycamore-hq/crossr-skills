# Verification

In a fresh activation the following six behaviors are directly observable and scorable:

- The agent recites the ocaml book's One-Sentence Mandate before generating or planning any OCaml code.
- The agent loads the topic reference that matches the situation, not the whole book, and does not feed How to an adversary.
- The agent applies combinators → match/guards → helper extraction as a fail-closed order: no `match` / `function` / branching `if` inside any arm of a `match` or `function` (a guard-shaped `if cond then Error e else Ok ()` under `->` included), no `match` under `then` / `else` even at the top of a function, no identity `| Error e -> Error e`, and `let*` meaning `Result.bind` / `let**` meaning `Option.bind` in every file.
- The agent defines or extends dedicated error variants per module, layer, or operation family returned as `result` values, and never uses exceptions as control flow, `Obj.magic`, `List.hd` / `List.tl`, unchecked `Option.get` / `Result.get_ok`, catch-all `try`, or `[@warning]` suppressions in production paths.
- The agent parses wire strings into domain types at the adapter edge, replaces sentinels and unlabeled booleans with variants and labeled arguments, matches exhaustively on owned variants, and exposes the surface through a `.mli` with abstract `type t` declared at the top of the `.ml` before any `let`.
- The agent enforces `dune build @check @fmt @runtest` (or the documented no-formatter gate) with zero warnings before calling the change complete, and refactors shadowed bindings, `;;`, objects-by-default, decorative functors, file-level `open List`, and missing `Fun.protect` on sight.

Violations against any of these six during fresh activation mean the book was not followed.
