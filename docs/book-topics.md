# Book topic prefix registry

Humans allocate prefixes here. The extractor does **not** read this file as a closed set. A book may mint a prefix the rust book does not use. Sharing a prefix across books is optional.

## Baseline (rust)

| Prefix | Topic | Book |
|---|---|---|
| RE | error-handling | rust |
| RP | input-parsing | rust |
| RD | type-system | rust |
| RL | layering | rust |
| RF | control-flow | rust |
| RT | testing | rust |
| RA | api-surface | rust |
| RC | tooling | rust |
| RS | safety-performance-and-security | rust |
| RY | tokio-runtime | rust |

Later books append rows. Do not reuse a prefix for a different idea inside one book.

## ocaml

Shares the baseline prefixes for the same ideas. Mints `RM`. Has no `RD`: OCaml's type surface is the `.mli` and lives under `RA`.

| Prefix | Topic | Book |
|---|---|---|
| RE | error-handling | ocaml |
| RP | input-parsing | ocaml |
| RL | layering | ocaml |
| RF | control-flow | ocaml |
| RM | monads | ocaml |
| RT | testing | ocaml |
| RA | api-surface | ocaml |
| RC | tooling | ocaml |
| RS | safety-performance-and-security | ocaml |
