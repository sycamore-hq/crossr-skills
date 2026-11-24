# Layering

Stratified modules. Calculations pure. Actions at the edges.

## Rules

RL-01  Code is organized into stratified layers via submodules and directories: primitives and data types lowest, domain calculations and combinators in the middle, orchestration of actions (I/O, side effects) highest.

RL-02  Functions at the same layer use the same level of abstraction.

RL-03  Data is immutable by default. `ref`, `mutable` fields, and `Buffer` are actions and belong only at the edges.

RL-04  Dependency order in `dune` libraries mirrors the layering: a lower layer never depends on a higher one.

RL-05  No `Util` / `Helpers` / `Common` modules. Name the actual thing (`String_ext`, `Json_codec`).
       check: rg --files -g '{util,utils,helpers,common}.ml' → 0

RL-06  Functors only for a demonstrated need for parameterized behavior, never for decoration.

RL-07  One compilation unit, one responsibility. File `user_profile.ml` is module `User_profile`.

## How

A handler that decodes JSON, queries the store, and renders the response is three layers pretending to be one. Split it: adapter in, calculation, adapter out.

Calculations take data and return data. They do not touch the clock, the disk, or a socket. Actions do, and they call calculations — never the other way round.

`code-writer` already owns this split. This topic is the OCaml shape of it: records and variants as data, functions without `ref` / I/O as calculation, adapters as action, and a `dune` `libraries` list that reads bottom-up.

A functor that only renames a module is decoration. A functor over a real parameter (a hash, a store backend) is the tool.

Structure between modules is the cross-cutting `deep-modules` book (`MD-01`..`MD-08`). In OCaml the compiler already forbids cycles between compilation units, so `MD-01` bites at the library level (`dune` libraries that need each other) and `MD-02` at mutually recursive modules. An abstract `type t` in the `.mli` (`RA-02`) is the usual cure for `MD-03`; an `.mli` that lists most of the `.ml` is an `MD-04` finding.
