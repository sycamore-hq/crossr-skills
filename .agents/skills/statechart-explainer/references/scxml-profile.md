# SCXML profile

The chart is valid W3C SCXML 1.0 (https://www.w3.org/TR/scxml/). This
profile is the subset the checker accepts and the template renders and
runs. It adds provenance in a foreign namespace, which SCXML allows.

## Skeleton

```xml
<?xml version="1.0" encoding="UTF-8"?>
<scxml xmlns="http://www.w3.org/2005/07/scxml"
       xmlns:crossr="https://sycamore-hq.github.io/crossr/scxml/1"
       version="1.0" datamodel="ecmascript"
       name="order-payment" initial="draft">
  <datamodel>
    <data id="paymentCaptured" expr="false"/>
  </datamodel>

  <state id="draft" crossr:source="src/order.rs:41">
    <transition crossr:id="t-submit" event="order.submit" target="pending"
                crossr:source="src/order.rs:88"/>
  </state>

  <state id="pending" crossr:source="src/order.rs:42">
    <transition crossr:id="t-confirm" event="order.confirm" cond="paymentCaptured"
                target="paid" crossr:source="src/order.rs:120"/>
    <transition crossr:id="t-timeout" event="timer.expired" target="cancelled"
                crossr:source="src/jobs/expire.rs:17"/>
    <onentry>
      <send event="timer.expired" delay="30min" id="expiry"/>
    </onentry>
  </state>

  <final id="paid" crossr:source="src/order.rs:43"/>
  <final id="cancelled" crossr:source="src/order.rs:44"/>
</scxml>
```

## Elements

| Element | Rules |
| --- | --- |
| `<scxml>` | `version="1.0"`. `name` is the machine id. `datamodel` is `null` or `ecmascript`. `initial` optional; default is the first child state. |
| `<state>` | `id` required. Atomic when it has no child states. Compound otherwise. `initial` attribute or `<initial>` child optional. |
| `<parallel>` | `id` required. Each child is a region that runs at the same time. |
| `<final>` | `id` required. Entering it raises `done.state.<parent-id>`. |
| `<history>` | `id` required. `type="shallow"` or `"deep"`. One default `<transition>`. |
| `<transition>` | `crossr:id` required and unique. `event` is a space-separated list; omit it for an eventless transition. `target` is a space-separated id list; omit it for a targetless transition. `type="internal"` allowed. |
| `<datamodel>` / `<data>` | One `<data id expr>` per condition. `expr` is `true` or `false`. |
| `<onentry>` / `<onexit>` / transition body | Executable content below. |

## Ids

- State ids are XML ids: start with a letter or `_`; then letters, digits,
  `_`, `-`, `.`. Use the code's names (`awaiting_payment`).
- Event names are dotted lowercase tokens (`order.pay`, `socket.closed`).
  SCXML matches prefixes: `event="error"` matches `error.network`.
- `crossr:id` on transitions is `t-` plus a short kebab name. Keep it stable
  across reruns. The prose JSON keys transitions by it.

## Conditions

`cond` is a small boolean language, so the page can run it without `eval`:

```
expr := term ('||' term)*
term := factor ('&&' factor)*
factor := '!' factor | '(' expr ')' | 'true' | 'false' | In('state-id') | data-id
```

In the XML file, write `&&` as `&amp;&amp;`.
Each `data-id` must be declared in `<datamodel>`. Use `datamodel="ecmascript"`
when any `cond` names data. This grammar is valid ECMAScript, so a real
SCXML interpreter runs the same chart.

## Executable content

The template runs these:

| Element | Effect in the page |
| --- | --- |
| `<raise event="x"/>` | Queues an internal event. |
| `<send event="x"/>` | Queues an external event after the current step. |
| `<send event="x" delay="5s" id="k"/>` | Adds a timer button the reader can fire. |
| `<cancel sendid="k"/>` | Removes that timer. |
| `<assign location="flag" expr="true"/>` | Sets a condition. `expr` is a condition expression. |
| `<log label="..." expr="'text'"/>` | Writes to the page log. |

Other elements (`<script>`, `<invoke>`, `<foreach>`, `<if>`) are valid
SCXML, but the page shows them as text and does not run them. Do not use
them to carry meaning the reader needs.

## Provenance

`crossr:source` is required on every `<state>`, `<parallel>`, `<final>`,
`<history>`, and `<transition>`. Format: `path:line` or
`path:start-end`, path relative to the repository root. Several locations
are separated by a comma.

## Checker rules

`scripts/check_statechart.py` fails on:

- XML that does not parse, or a root that is not SCXML 1.0.
- Missing or duplicate state ids or `crossr:id` values.
- A `target`, `initial`, or `In()` that names no state.
- An `initial` that is not a descendant of its state.
- A `cond` outside the grammar, or one that names undeclared data.
- A missing `crossr:source`.
- A `<history>` with a type other than `shallow` or `deep`.

It warns on:

- States that no transition or initial path enters.
- Non-final atomic states with no outgoing transition (dead ends).
