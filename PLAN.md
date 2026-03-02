# CCC - Verbs & Practice Modes Plan

A comprehensive plan for evolving the CCC flashcard system to support verbs from JSON, phrases, and multiple practice modes.

---

## 1. Data Sources

### A. `verbs/*.json` — Conjugation Source of Truth

Existing structure. Contains:
- `indicativo`: presente, preterito, imperfecto, futuro, condicional, presentePerfecto, etc.
- `subjuntivo`: presente, imperfecto, pluscuamperfecto
- `afirmativo` / `negativo`: imperativo
- `english`: infinitivo, gerundio, participioPasado, tense descriptions
- Reflexive verbs have their own files (irse.json, comerse.json) with full conjugations including reflexive pronouns

**Editable:** The verb JSONs are ours to edit. When the canonical data has translations or forms we prefer to change (e.g., "to request" → "to ask"), we edit the JSON directly. This keeps `verbs.csv` minimal.

### B. Phrases / Idioms — New Data Source

For items that aren't just conjugated verbs:

| Type | Examples | Storage |
|------|----------|---------|
| Reflexive with changed meaning | irse=to leave, comerse=to eat up, tomarse=to drink up | `verbs/*.json` (own file) |
| Idiomatic phrases | echar la mano=to give a hand | `phrases.json` or `data/phrases.txt` |
| Accidental se | se me cayó | Construction + verb JSON |
| "Se fue" style | to go away suddenly | Reflexive verb JSON + usage note |

**Recommendation:** Create `phrases.json` (or `phrases.csv`) for idiomatic phrases:

```json
[
  {"phrase": "echar la mano", "definition": "to give a hand", "verb_base": "echar"},
  {"phrase": "echar de menos", "definition": "to miss"}
]
```

Reflexive variants (irse, comerse, tomarse) = separate verb JSON files in `verbs/`.

---

## 2. `verbs.csv` — Verb Roster & Practice Flags

**Settings and preferences only—never conjugations.** The CSV controls which verbs to include and how to display them (e.g., present style). All conjugation data comes from `verbs/*.json`.

| Column | Purpose | Values |
|--------|---------|--------|
| `verb` | Verb (or phrase) to include | `ir`, `irse`, `hablar`, `echar_la_mano` |
| `presente` | Practice present indicative | 1/0 |
| `preterito` | Practice preterite | 1/0 |
| `subjuntivo` | Practice subjunctive (with triggers) | 1/0 |
| `commands` | Practice imperativo (afirmativo, negativo) | 1/0 |
| `dop` | DOP practice (transitive verbs) | 1/0 |
| `iop` | IOP practice (le, a ella) | 1/0 |
| `questions` | Flip-subject questions (present) | 1/0 |
| `es_present_style` | Present tense display preference | `simple` / `progressive` |

- Default missing columns to 0 for backward compatibility.
- Prefer editing verb JSONs for translation/irregular overrides (e.g., `thirdPersonSingular`, infinitivo). CSV stays minimal.

---

## 3. `constructions.json` — Periphrastics & Compounds

Defines compound constructions. Structure:

```json
{
  "periphrastics": [
    {"helper": "poder", "form": "infinitive", "meaning": "can/to be able to"},
    {"helper": "soler", "form": "infinitive", "meaning": "to usually"},
    {"helper": "haber", "form": "participle", "meaning": "to have done"},
    {"helper": "deber", "form": "infinitive", "meaning": "must/should"},
    {"helper": "acabar", "form": "infinitive", "meaning": "to have just"},
    {"helper": "dejar", "form": "infinitive", "meaning": "to stop/to let"},
    {"helper": "andar", "form": "gerund", "meaning": "what I'm doing right now"},
    {"helper": "seguir", "form": "gerund", "meaning": "to still be / to keep"},
    {"helper": "volver", "form": "infinitive", "meaning": "again"},
    {"helper": "llevar", "form": "gerund", "meaning": "have been -ing", "haber_estado_flag": true}
  ],
  "modals": [
    {"expr": "querer", "meaning": "to want to"},
    {"expr": "hay que", "meaning": "one must"},
    {"expr": "tener que", "meaning": "to have to"}
  ]
}
```

- `haber_estado_flag`: for llevar + gerund → equivalent to haber + estado + gerund (present and imperfect "had been").

---

## 4. Practice Modes (Order of Implementation)

| # | Mode | Notes |
|---|------|-------|
| 1 | Present indicative | Current |
| 2 | Preterite | Current |
| 3 | llevar + gerund | With haber_estado_flag for "had been" |
| 4 | DOP | "He told me", "I prohibit you"; DO pronoun required when DO comes before verb |
| 5 | Questions | Present tense, flip subject |
| 6 | Commands | Positive and negative (afirmativo, negativo) |
| 7 | IOP | le, a ella; IOP always |
| 8 | Periphrastics | poder, soler, haber, deber, acabar, dejar, andar, seguir, volver, llevar |
| 9 | Subjunctive | With random triggers (si..., cuando...) |
| 10 | Present perfect | haber + participle |
| 11 | Progressive tenses | estar + gerund variants |
| 12 | Modals | querer, hay que, tengo que |

### DOP/IOP Rules (from notes)
- DOP: Required when DO comes before verb (e.g., "el libro lo di a juan")
- IOP: Always (e.g., "di el libro a juan" → le, a ella)

---

## 5. Reflexive / Idiomatic Variants

| Category | Examples | Approach |
|----------|----------|----------|
| Different meaning | irse, comerse, tomarse | Own verb JSON (irse.json, etc.) |
| Se accidental | se me cayó | Construction + verb JSON |
| "Se fue" | to go away suddenly | Note in irse.json |
| Idioms | echar la mano | phrases.json |

**Reflexive verbs list (from notes):**
- levantar→levantarse, despertar→despertarse, acostar→acostarse, duchar→ducharse, bañar→bañarse, lavar→lavarse, cepillar→cepillarse, peinar→peinarse, afeitar→afeitarse, vestir→vestirse
- divertirse, enojarse, alegrarse, caerse, preocuparse, encontrarse, acercarse
- ponerse (to try on, to become sad), quedarse (to stay), dormirse (fall asleep), sentirse (to feel), morirse (figuratively), volverse (to turn crazy), olvidarse (to forget), despertarse (to wake up)
- comerse (to eat up), tomarse (to drink up)

---

## 6. Code Architecture

```
verbs.py
├── load_verb_json(verb) → dict
├── load_phrases() → list (if phrases.json exists)
├── load_constructions() → dict (constructions.json)
├── generate_present_cards(verb_data, prefs) → List[Tuple]
├── generate_preterite_cards(verb_data, prefs) → List[Tuple]
├── generate_subjunctive_cards(verb_data, prefs) → List[Tuple]
├── generate_command_cards(verb_data, prefs) → List[Tuple]
├── generate_dop_cards(verb_data, prefs) → List[Tuple]
├── generate_iop_cards(verb_data, prefs) → List[Tuple]
├── generate_question_cards(verb_data, prefs) → List[Tuple]
├── generate_periphrastic_cards(helper_verb, main_verb_data, ...) → List[Tuple]
├── generate_modal_cards(...) → List[Tuple]
├── generate_present_perfect_cards(verb_data, prefs) → List[Tuple]
├── generate_progressive_cards(verb_data, prefs) → List[Tuple]
└── generate_verbs_flashcards(csv_path, output_path)
    → reads CSV, calls generators based on flags, writes to data/verbs.txt
```

---

## 7. Deck Strategy

- **Option A:** Single `data/verbs.txt` (all card types)
- **Option B:** Multiple decks: `verbs_present.txt`, `verbs_subjunctive.txt`, etc.
- **Option C:** Single deck with mode tags; app filters at runtime

**Recommendation:** Start with single deck; split later if needed.

---

## 8. Implementation Phases

| Phase | Scope | Status |
|-------|--------|--------|
| **Phase 1** | JSON as source; slim CSV; present + preterite only | ✅ Done |
| **Phase 2** | Subjunctive, commands | Next |
| **Phase 3** | DOP, IOP | |
| **Phase 4** | Questions | |
| **Phase 5** | Periphrastics (constructions.json) | |
| **Phase 6** | Present perfect, progressive tenses | |
| **Phase 7** | Modals (querer, hay que, tener que) | |
| **Phase 8** | Phrases/idioms; reflexive variants | |

---

## 9. Phase 1 Completed (Current State)

### What We Did

**Architecture:**
- `verbs.csv` slimmed to 2 columns only: `verb`, `es_present_style` — settings/preferences only, never conjugations
- Flashcard generation reads from `verbs/*.json`; CSV controls which verbs and present style
- `verbs.py` loads JSON, extracts Spanish from `indicativo.presente`/`preterito`, English from `english.*`

**JSON edits (to match our preferences):**
| Verb | Change |
|------|--------|
| pedir | infinitivo: "to ask"; gerundio: "asking"; full indicativo/subjuntivo/imperativo |
| saber | infinitivo: "to know" (was "to know (information)") |
| decir | infinitivo: "to say" (was "to say, tell") |
| irse | infinitivo: "to leave"; gerundio: "leaving"; preterito: "I left" (was "going away" / "went away") |
| tener | Added `english.thirdPersonSingular: "has"` for irregular 3rd person |

**Code:** `_get_3rd_person()` checks `json_data.english.thirdPersonSingular` before deriving (fixes "he haves" → "he has").

**Naming conventions:** irse = "leave" / "leaving"; salir (future) = "go out" / "going out" — no conflict.

### Next Steps (Phase 2+)

1. **Phase 2** — Subjunctive, commands: Add flags to CSV; implement `generate_subjunctive_cards()` and `generate_command_cards()` using `subjuntivo`, `afirmativo`, `negativo` from JSON.
2. **Phase 3** — DOP, IOP: Add dop/iop flags; implement pronoun variants.
3. **Phase 4** — Questions: Flip-subject question cards.
4. **Phase 5** — Create `constructions.json`; implement periphrastics (poder, soler, llevar, etc.).
5. **Phase 6** — Present perfect (haber + participle), progressive tenses.
6. **Phase 7** — Modals (querer, hay que, tener que).
7. **Phase 8** — phrases.json for idioms; expand reflexive roster.

---

## 10. Verb Roster (from notes)

**Regular/common verbs:**
ser, escoger, estar, empezar, venir, querer, leer, jugar, salir, dormir, volver, pensar, seguir, conocer, manejar, oír, servir, elegir, mirar, escuchar, ayudar, alcanzar, buscar, aprender, parecer, entender, doler, permitir, recibir, abrir, comprar, tirar, echar, dirigir, construir, creer, exigir, sentir, morir, conseguir, quedar, tomar, gustar, trabajar, llamar, oler, dejar, subir, recordar, ganar, insistir, sufrir, explicar, arrepentirse, quejarse, mandar, marcar, añadir, tocar, inclinarse, creer

**Reflexive / special meaning:**
ponerse, quedarse, dormirse, sentirse, morirse, volverse, olvidarse, despertarse, levantarse, acostarse, ducharse, bañarse, lavarse, cepillarse, peinarse, afeitarse, vestirse, divertirse, enojarse, alegrarse, caerse, preocuparse, encontrarse, acercarse, irse, comerse, tomarse

**Idioms (phrases):**
echar la mano (to give a hand), etc.

---

## 11. Open Questions

1. **phrases.json structure** — JSON vs CSV; or reuse `data/phrases.txt` term/definition format.
2. **Subjunctive triggers** — Store trigger phrases (si..., cuando...) in config vs. randomize at runtime.
3. **Se accidental** — Treat as separate construction; flag which verbs support it.
4. **Deck split** — When to split into multiple decks vs. single deck.

---

*Last updated: March 2025*
