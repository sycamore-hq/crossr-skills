# Specialization

Precondition: the work adds or reshapes modules, types, fields, public functions, files or directories, with `plan-writer` active at plan time or `code-writer` active outside the plan loop.

This book supplies the structural discipline between modules and types: dependency order between siblings, loops between things, data hidden behind its owner, interfaces smaller than their bodies, and the layout limits that warn early. It does not restate `code-writer`'s function-level rules or the `system-design` book's plan-level rules on boundaries and invariant ownership; `MD-03` is the code-level form of `system-design/DB-03`.

It is a cross-cutting book (`metadata.scope: "cross-cutting"`). The harness discloses it alongside whichever language book the PBI selects, never in place of one. It names no language. The `rust` and `ocaml` books supply the idioms that realize its rules.

It is not a writing skill. `unslop` strips AI tells from prose; comment categorization and cleanup belongs to `code-writer` and `code-review`. Neither overlaps this book.

Postcondition: combined output satisfies the active card (`plan-writer` or `code-writer`) + the language book + this book with zero contradictions.
