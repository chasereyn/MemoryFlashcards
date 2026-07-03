# Storage format

## Overview

Deck **content** and review **progress** live in separate folders.

| File | Purpose | Edit by hand? | Git |
|------|---------|---------------|-----|
| `data/decks/{name}.tsv` | Card content (`term`, `definition`) | Yes | Tracked |
| `data/progress/{name}.tsv` | Review metadata keyed by `id` | No | Gitignored |

## Content file (`data/decks/*.tsv`)

Tab-separated, one card per line:

```
term	definition
Roof	Tejado
Step aside!	Golpe avisa!
```

- Header row `term\tdefinition` is optional but recommended
- Card `id` is MD5 hash of `term|definition` (same as legacy system)

## Progress file (`data/progress/*.tsv`)

First line: `# last_session_date: YYYY-MM-DD`

Then header + one row per card with review metadata only (term/definition come from the deck file on sync).

## Sync (`storage.sync_deck`)

On startup:

1. Parse content TSV → card list
2. Load progress TSV → metadata by `id`
3. **Preserve** metadata for cards in both
4. **Add** new cards from content (default metadata)
5. **Remove** progress rows for cards deleted from content
6. Save progress TSV

Run tests: `python test_sync.py`
