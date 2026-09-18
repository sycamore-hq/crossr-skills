# Cursor model ids (loaded on demand)

Load this file only when the harness is Cursor. Other harnesses disclose
their own map. The conductor card keeps `--model-review` / `--model-fix`
as parameters; this page is the slug table, not a second law.

## `--model-review`

Short ids map to Claude Fable 5.1 thinking slugs. Default (no flag, or
`high`) is Fable 5.1 high.

| id | slug |
|---|---|
| `low` / `medium` / `high` / `xhigh` / `max` | `claude-fable-5-1-thinking-<id>` |
| same + `-fast` | `claude-fable-5-1-thinking-<id>-fast` |

Any other token is a raw slug.

## `--model-fix`

No short map. The token is a raw slug (example: the Desktop slug for
Kimi K3 Max). Default (no flag) is the user's default model.

## Missing from this session

Review Agent — stop and ask. Fix Agent — use the user's default and say
so once. Same stop rules as the card.
