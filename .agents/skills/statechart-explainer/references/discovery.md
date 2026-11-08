# Discovery: find and extract state machines

A state machine is a value with a finite set of named states, events that
change it, and behavior that depends on it. Some code declares this. Most
code does not.

## Explicit machines

The code declares states and transitions in one place. Search for:

| Ecosystem | Signals |
| --- | --- |
| JS / TS | `xstate` (`createMachine`, `setup`), `@xstate/fsm`, `robot3`, `javascript-state-machine`, `typestate`; reducers that `switch (state.status)` |
| Python | `transitions` (`Machine(`), `python-statemachine` (`StateMachine`, `State(`), `django-fsm` (`FSMField`, `@transition`), `viewflow` |
| Ruby | `aasm`, `state_machines`, `workflow`, `statesman` |
| Java / Kotlin | Spring Statemachine (`StateMachineConfigurerAdapter`), Squirrel, `enum` with `next()` methods, Akka `FSM`, `AbstractBehavior` switching `Behavior` |
| C# | `Stateless` (`StateMachine<`, `.Permit(`), Automatonymous, MassTransit sagas |
| Rust | `statig`, `rust-fsm`, `sm`, `machine!`; typestate structs (`Conn<Open>`); `enum State` + `match (state, event)` |
| Go | `looplab/fsm`, `qmuntal/stateless`; `type State int` + `iota` + `switch` |
| Erlang / Elixir | `gen_statem`, `gen_fsm`, `:state_timeout` |
| C / C++ | Boost.MSM, Boost.SML, `QStateMachine`, state tables (`transition_table[][]`), `switch (state)` in a loop |
| Config / IaC | AWS Step Functions (`States`, `StartAt`), Temporal and Cadence workflows, Argo, GitHub Actions job `needs`, Kubernetes conditions |
| Data | DB columns named `status`, `state`, `phase`, `stage`, `step`, `lifecycle`; `CHECK (status IN (...))`; enum types in migrations |
| Existing charts | `*.scxml`, `*.puml` with `[*] -->`, Mermaid `stateDiagram`, Graphviz files with state names |

## Implicit machines

Nothing declares the machine. The behavior still depends on a finite state.
Search for:

- **Status fields.** One field of enum, string, or int type with three or
  more writes in different functions, and reads that guard behavior
  (`if order.status == "paid"`).
- **Flag clusters.** Two or more booleans that change together and that
  code reads together: `isLoading`, `isError`, `hasData`; `connected`,
  `authenticated`; `started`, `stopped`. Some combinations never occur. The
  combinations that occur are the states.
- **Order rules.** Methods that throw or return early when called out of
  order: `if !self.initialized`, `assert(opened)`, "called before start".
- **Nullable stages.** Optional fields that fill in a fixed order
  (`submitted_at`, then `approved_at`, then `shipped_at`). The set of filled
  fields is the state.
- **Loops with modes.** Parsers, lexers, retry loops, back-off, and
  reconnect loops that keep a mode, attempt counter, or phase.
- **UI flows.** Wizards, multi-step forms, modals with steps, routes guarded
  by progress, components with `step` or `view` state.
- **Protocols.** Handshakes, sessions, leases, locks, sagas, and jobs with
  queued, running, retrying, done, and failed phases.

Search tips: grep for the field name with `=`, `:=`, `set`, `update`,
`.status =`, and SQL `UPDATE ... SET status`. List every write. Then list
every read inside an `if`, `match`, `switch`, guard, or `WHERE`.

## Keep or reject

Keep a candidate when all are true:

1. It has two or more states.
2. It has one or more transitions.
3. Some behavior depends on the current state.

Reject, and record the reason, when:

- The value is only displayed or stored and nothing branches on it.
- The "states" are a free-form label set by users.
- It is a counter with no thresholds that change behavior.

Merge candidates that are one lifecycle in different layers. Keep the layer
that enforces the rules as the source of the chart. Put the other layers in
`evidence`. When the layers disagree, write a note that names the
difference.

## Extract the model

For each kept machine:

1. **States.** Use the names in the code. For a flag cluster, name each
   reachable combination after what it means (`loading`, `failed`), and
   note which flag values make it.
2. **Initial state.** The value at construction, at insert, or in the
   default. When code sets it in more than one place, model the one that
   runs first and note the others.
3. **Events.** One event per function, handler, message, or endpoint that
   writes the state. Name the event after that function or message
   (`order.pay`, `socket.closed`). Time-based writes use a timer event and
   an SCXML `<send delay>`.
4. **Source states.** For each write, find the guard that encloses it. The
   guard names the source states. A write with no guard is a transition
   from every state. Model it on the parent compound state and add a note,
   because it is often a defect.
5. **Conditions.** Each extra boolean check on a write becomes a named
   condition in the data model (`cond="paymentCaptured"`). Name it after
   what it checks, not after the variable.
6. **Actions.** Side effects that run on the transition (send email, emit
   event, write audit row) go in the transition body. Effects that run on
   each entry go in `<onentry>`.
7. **Hierarchy.** When several states share outgoing transitions (`cancel`
   from any open state), make a compound state for them. Use `<parallel>`
   only when the code keeps two independent state values for one entity.
8. **Final states.** States with no outgoing transitions that end the
   lifecycle. A state with no outgoing transitions that should not end it is
   a dead end. Write a note.
9. **Source.** Put `crossr:source="path:line"` on each state (the place the
   state is defined or first set) and each transition (the write).

## Defects to report

These come out of the model. Report them. Do not fix them.

- Unreachable state: defined but no transition enters it.
- Dead end: not final, no way out.
- Any-state write: a write with no guard on the source state.
- Layer mismatch: the database allows a state the API never writes, or the
  reverse.
- Race: two writers with no lock or version check on one field.
