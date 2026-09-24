# Control flow

Flat, fail-closed. Nested `match` is a violation, not a style nit. Combined discriminant replaces nesting; it does not license a match inside an arm. Monad operators are RM's; wire strings are RP's.

## Rules

RF-01  Flat code, strict fail-closed priority: (1) stdlib combinators and pipelines (`|>`, `Option.map` / `bind` / `to_result`, `Result.map` / `bind` / `map_error`, `List.filter_map` / `map` / `iter` / `fold_left`); (2) early `match` / guard on a domain variant, `function`, or `if cond then Error e else Ok ()`; (3) a small private helper (`let rec` only for genuine recursion).

RF-02  Nested `match` is a violation. No arm of a `match` or `function` contains another `match`, `function`, or branching `if`. An `if` under `->` is extracted even in the RF-01 guard shape (`if cond then Error e else Ok ()`). `then` / `else` never contain a `match`, including `if cond then match` at the top of a function: write `match cond, x with`, or a guard that returns `Error` / `Ok`.
       `function` under `then` / `else` is legal at the top of a function and a violation inside an arm. Combined discriminant (`match a, b with`) replaces nesting. Flatten onto the product or extract the inner case to a named helper (RF-03).
       A hit is a violation. Zero hits leaves these violations uncaught: `|`, `with`, or `function` on a different line from `->`; a `let`, a comment, or a `;` sequence between `->` and the keyword.
       check: rg -U --glob '*.ml' '(?:\|[^\n]*->|\bwith[^\n|]*->|\bfunction[^\n|]*->)\s*\(?\s*(begin\s+)?(match|function|if)\b|(then|else)\s*\(?\s*(begin\s+)?match\b' → review each hit; every hit is a violation, and zero hits does not certify

RF-03  Actions may branch and sequence. Adapter and UI action code flattens by extracting each branch into a named helper, not by forcing pipelines onto statements. Nested `match` is still a violation: helpers, not another match inside an arm.

RF-04  Identity matches are a violation: `| Error e -> Error e`, `| Ok v -> Ok v`, `| None -> None`, `| Some v -> Some (f v)`. Use `Result.map` / `Option.map`.
       check: rg 'Error e -> Error e|Ok v -> Ok v|None -> None' --glob '*.ml' → 0

RF-05  Function body ≤ 30 lines. Over that, extract a helper before finishing.

RF-06  Max 5 parameters. Beyond that, or when two parameters share a type, use labeled arguments and/or a record. Label whenever order is ambiguous. Never an unlabeled boolean — use a variant (`type visibility = Visible | Hidden`).

RF-07  Data-structure argument last so `|>` reads left to right (stdlib convention: `List.fold_left`, `List.map`).

RF-08  Every `match` is exhaustive. On a variant this module owns, never a catch-all `_` — a new constructor must fail the build. `_` only for leftover / extension cases, with a comment stating why the rest are safe to ignore.

RF-09  Multi-dimensional dispatch carve-out: a catch-all is allowed only when one match covers several owned dimensions (role × action × resource) and only as deny-closed dispatch (`| _ -> false` / `| _ -> None`) with a comment stating deny-by-default. A catch-all that grants access or returns data is a violation.

RF-10  Explicit variant constructors over boolean flags and sentinel values. `match` over nested `if/else` when discriminating on data.

RF-11  Never shadow a binding (`let x = ... in let x = ...`). Distinct concepts get distinct names.

RF-12  Destructure rather than project: `let { field; _ } = r`, not `r.field`, when several fields are used.

RF-13  `=` / `<>` (or `equal` on `t`). Physical `==` / `!=` only with a comment stating why pointer equality is required.
       check: rg ' == | != ' --glob '*.ml' → review each hit

RF-14  `for` over arrays and strings; recursion for anything with an early exit or a result. A `while` loop carries an explicit invariant. Sequences inside `if` / `else` are grouped with `begin` / `end`.

RF-15  Use stdlib iterators. Do not encode everything as `fold_*`, and never reimplement `List.map` / `List.iter` by hand.

RF-16  Single responsibility per function.

## How

The order is fail-closed: reach for a combinator, and only when none fits, a guard, and only then a helper.

```ocaml
let* team = Store.find_team ~id |> Option.to_result ~none:No_such_team in
let* () = if Team.is_open team then Ok () else Error Team_closed in
Ok (Team.roster team)
```

Bad — a `match` or `if` inside any arm, including a product match:

```ocaml
match Store.find_team ~id with
| None -> Error No_such_team
| Some team ->
  if Team.is_open team then (match roster team with ...) else Error Team_closed

match (verb, write) with
| Plan, Plan_saved t -> saved t
| Goals, _ -> (
    match write with
    | Plan_saved t -> active t
    | _ -> no_plan)
```

Combined discriminant (`match a, b with`) replaces nesting. A match inside an arm is still nesting. `if cond then match` at the top of a function is the same violation. The RF-01 guard (`if cond then Error e else Ok ()`) is legal as the function body, and under `->` it is extracted. `if cond then function` at the top of a function is legal. `function` inside an arm is nesting.

`fun x -> match x with` at the top of a function is the good form (RF-01). The grep misses a `let`, a comment, or a `;` sequence between `->` and the keyword, and a pattern whose `|`, `with`, or `function` sits on a different line from `->`. Those are still violations.

Action code (an HTTP handler, a store-row decoder) legitimately branches on data. There, each branch becomes a named helper; the handler reads as a table of cases. Nested `match` is still a violation there.

A catch-all on an owned variant means a new constructor compiles silently and misroutes at runtime. The deny-closed carve-out exists because an authorization table over three dimensions cannot enumerate every cell — and even there `| _ -> true` is a hole.
