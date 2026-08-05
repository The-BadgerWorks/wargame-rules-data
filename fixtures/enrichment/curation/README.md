<!-- AI-Assisted: Claude Code (model: claude-opus-5) - Documented the synthetic authored-summary
     fixture set (004 task T042). The records themselves carry no comment: every `curation/`
     schema is `additionalProperties: false`, so a `_comment` key would fail the very validation
     the fixtures exist to exercise. The explanation therefore lives here, as it does for the
     repository's own `curation/` tree. -->
# `fixtures/enrichment/curation/`

Authored records in **mixed review states**, for the four summary classes. Every faction, rule
name, summary, and digest here is invented. Nothing is a rewording of anything — there is nothing
upstream to reword, because these factions do not exist.

## `faction-rules/` (US3, task T042)

The set exists to make one distinction testable that a bare array cannot express (FR-021): a
faction with **no army rule** and a faction **nobody has curated yet** are different facts.

| File | `army_rule_state` | Carries | Why it is here |
|---|---|---|---|
| `f-glimmerfen-covenant.json` | `present` | `approved` + `draft` | Two rules on one faction — which is why `display_order` exists — in different states, so a gate is proven to name the *entries* it blocks on rather than the faction |
| `f-bracklight-host.json` | `present` | `in_review` | Authored and offered, not signed off. Blocks for a **different reason** from a missing record, and the two codes stay distinct because a curator needs to know which one to act on |
| `f-sedgeward-conclave.json` | `present` | `needs_rereview` | The pipeline never *writes* this state — it recomputes it every run from a moved digest — but a curator can set it by hand, and it must block on the same terms either way |
| `f-mirefen-enclave.json` | `none` | *(no rules)* | The curated **negative**: contributes nothing to the coverage denominator and is not outstanding work. A finished decision, not a gap |
| *(no file)* `f-ashen-vigil` | — | — | The third state, expressed by **absence**: not yet curated. Counted as outstanding, and deliberately not represented by a file, because representing it by one is exactly the conflation FR-021 forbids |

## `detachment-rules/` (US4, task T051)

A **bare array** per faction, keyed by the rule rather than by the detachment, because a
detachment may own more than one. The set exists to make the three keying edge cases of
data-model.md §2.2 testable, and each row below is one of them.

| File | Record | State | Why it is here |
|---|---|---|---|
| `f-glimmerfen-covenant.json` | `d-fenlight-vigil:veiled-advance` | `approved` | Half of the **shared rule name across factions** pair. Its digest carries forward while unchanged and flags only itself when moved |
| | `d-fenlight-vigil:massed-fire` | `draft` | A second rule on the **same detachment**, in a different state — the one-to-many relation, and proof a gate names entries rather than detachments |
| | `d-tidewalk-column:veiled-advance` | `approved` | The **same rule name on a second detachment of the same faction**: distinct key, distinct digest, distinct summary. A name-keyed store would collapse these two into one |
| `f-bracklight-host.json` | `d-bracklight-charge:veiled-advance` | `in_review` | The other half of the shared-name pair, in a **different faction and a different state** — so approving one can never approve the other |
| | `d-bracklight-charge:sundering-tide` | `needs_rereview` | Set by hand here; the pipeline never writes this state, it recomputes it from a moved digest every run |

A rule the source publishes with **no record in either file** is the fifth case and deliberately
has no fixture line, because it is expressed by absence: it still ships with its name, counts as
outstanding, and is named in the coverage report (FR-022).

The digests are invented 32-hex strings. That is enough: what the machinery asserts is that a
stored digest **equalling** a freshly computed one carries the approval forward and a stored
digest **differing** from it flags exactly that summary — a property of the comparison, not of
the hash. Computing a real digest would require real mechanic text, which is the thing this
repository never holds.
