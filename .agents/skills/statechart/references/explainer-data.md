# Explainer data

The page is the template plus two data blocks:

```html
<script type="application/scxml+xml" id="scxml">
  ... the SCXML file, unchanged ...
</script>
<script type="application/json" id="explainer">
  { ... the JSON below ... }
</script>
```

The SCXML must not contain the text `</script`. The checker verifies that
the embedded SCXML equals the `.scxml` file.

## JSON shape

```json
{
  "schema": 1,
  "title": "Order payment",
  "kind": "explicit",
  "confidence": "high",
  "repo": { "url": "https://github.com/acme/shop", "rev": "3f2c1ab" },
  "summary": [
    "This machine controls the payment of one order."
  ],
  "context": [
    "A customer puts items in an order. Then the customer pays for the order."
  ],
  "glossary": [
    { "term": "order", "definition": "A list of items that one customer wants to buy." }
  ],
  "states": {
    "draft": { "meaning": "The customer can add and remove items." }
  },
  "events": {
    "order.submit": { "meaning": "The customer sends the order.", "origin": "The checkout page." }
  },
  "conditions": {
    "paymentCaptured": { "meaning": "The bank took the money from the card." }
  },
  "transitions": {
    "t-submit": { "meaning": "The order stops changes and waits for payment." }
  },
  "scenarios": [
    {
      "name": "Normal payment",
      "goal": "Show how an order becomes paid.",
      "steps": [
        { "event": "order.submit", "caption": "The customer sends the order." },
        { "set": { "paymentCaptured": true }, "event": "order.confirm",
          "caption": "The bank takes the money. The order becomes paid." }
      ]
    }
  ],
  "evidence": [
    { "source": "src/order.rs:40-45", "note": "The `OrderStatus` enum names the states." }
  ],
  "notes": [
    { "title": "Cancel from any state", "text": "The admin endpoint sets `cancelled` with no check of the current state." }
  ],
  "related": [
    { "title": "Shipment", "href": "shipment.html" }
  ],
  "layout": {
    "order": ["draft", "pending", "paid", "cancelled"],
    "rank": { "cancelled": 2 }
  }
}
```

## Fields

| Field | Required | Rules |
| --- | --- | --- |
| `schema` | yes | `1`. |
| `title` | yes | The machine, named for a reader: "Order payment", not `OrderFsm`. |
| `kind` | yes | `explicit` or `implicit`. |
| `confidence` | yes when implicit | `high`, `medium`, or `low`. How sure you are that the chart matches the code. |
| `repo` | no | `url` and `rev`. The page links each `crossr:source` to `url/blob/rev/path#Lline`. |
| `summary` | yes | 1–3 paragraphs. What the machine controls and why it matters. |
| `context` | yes | 1–4 paragraphs. The domain background a stranger needs. No code. |
| `glossary` | yes | Each domain term and technical name the prose uses. |
| `states` | yes | One entry per state id, history ids included. `meaning` says what is true while the machine is in the state. |
| `events` | yes | One entry per event name in the chart. `meaning` says what happened. `origin` says who or what sends it. |
| `conditions` | when data exists | One entry per `<data id>`. `meaning` says what is true when the value is true. |
| `transitions` | yes | One entry per `crossr:id`. `meaning` says what changes and why. |
| `scenarios` | yes | One or more. Each step has `caption` and one or both of `set` and `event`. A step whose `event` has no effect is a self-check error. |
| `evidence` | yes when implicit | Why this code is a machine. |
| `notes` | no | Gotchas, defects, layer mismatches, open state sets. |
| `related` | no | Pages for machines this one talks to. |
| `layout` | no | Hints. See below. |

Every string in `summary`, `context`, `glossary[].definition`, `meaning`,
`origin`, `goal`, `caption`, `evidence[].note`, and `notes[].text` is
descriptive STE: 25 words a sentence, 6 sentences a paragraph. A string in
an array of paragraphs is one paragraph.

## Scenarios

Write scenarios that a newcomer needs to see: the normal path first, then
each failure path, then any path that a note warns about. Together they
should fire each transition at least once. The self-check banner lists
transitions no scenario fires as a warning.

## Layout

The template draws compound states as boxes that contain their children,
with children in rows from top to bottom. Without hints, the row of a state
is its distance from the initial state, and the order inside a row reduces
crossings.

- `layout.order`: state ids in the order you want them within their row.
- `layout.rank`: `{ "state-id": row }`, a row number inside the parent box.
  Use it to move a failure state down, or to put two states in one row.

Add hints only after you look at the page and see a crossing or a collision.
