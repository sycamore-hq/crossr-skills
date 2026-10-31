# Shared State

Separate before you serialize.

## Rules

DX-01  Before introducing locks, queues, or other serialization, the plan shows that the actors need the same mutable state. Otherwise it partitions the state or gives each actor its own.

DX-02  Every remaining piece of shared mutable state has a single structurally enforced mutation authority, through ownership, types, encapsulation, or non-bypassable synchronization. Conventions and advisory locks do not qualify.

DX-03  For each remaining piece of shared mutable state, the plan names its mutation authority, the structural mechanism that enforces it, and how other actors reach it: messages, immutable snapshots, or read-only interfaces.

## How

Default to removing the shared write target. Give each actor its own file, key, branch, or state directory, and merge only at the read or reporting boundary. Treat "we need a lock" as a design smell to check, not a default.

A database is shared mutable state. Ownership sits at the independently mutable unit: database, table, partition, row, aggregate, or record. Several writers are fine when each mutates only its own unit and that ownership is enforced, for example by database permissions. A transaction alone does not establish ownership: it gives atomicity and isolation, but still allows several independent writers.

A non-bypassable `Mutex<T>` that owns its data qualifies. It provides mutual exclusion rather than a designated owner, and both count as a mutation authority. It protects only the path that goes through it, so the plan rules out any other path: direct database writes, or a mutable alias exposed elsewhere.

For each surviving shared state, answer four questions:
1. Why can't it be partitioned or copied?
2. Who or what has mutation authority?
3. What structure prevents unauthorized or concurrent mutation?
4. How do other actors read it or request changes without bypassing that structure?
