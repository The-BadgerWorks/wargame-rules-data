<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Pinned the exact contract versions this
     repository serves, per Setup task T013. -->
<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - 006 T050: repointed the two frozen
     consumer contracts to the versions T040/T041 bumped them to (reference-db-schema.md v1.5.0,
     curated-snapshot-format.md v1.3.0) and added this feature's own now-governing
     loadout-schema-delta.md at 1.0.0 (frozen at T052). -->
# Contract versions this repository serves

This repository is bound by two kinds of contract: the **frozen consumer contracts** owned by
`001-army-builder-app` (which this repository may not redefine unilaterally), and **this
feature's own contracts**, which this repository's own `contracts/` directory (mirrored from
`specs/002-rules-data-pipeline/contracts/` in `WargameCompanion`) defines.

## Frozen consumer contracts (govern)

| Contract | Version | Source of truth |
|---|---|---|
| `reference-db-schema.md` | **v1.5.0** | `WargameCompanion:specs/001-army-builder-app/contracts/reference-db-schema.md` |
| `rules-data-manifest.md` | **v1.1.1** | `WargameCompanion:specs/001-army-builder-app/contracts/rules-data-manifest.md` |

These define the JSON snapshot bundle's shape and the manifest's shape respectively. Both are
owned by `001-army-builder-app`. A change to either is a **cross-feature versioning exercise** —
coordinated with the `001` maintainers and given a new version number there — never a unilateral
edit made from this repository.

## This feature's own contracts

| Contract | Version | Source of truth |
|---|---|---|
| `curated-snapshot-format.md` | **1.3.0** | `WargameCompanion:specs/002-rules-data-pipeline/contracts/curated-snapshot-format.md` |
| `validation-report.md` | 1.1.0 | `WargameCompanion:specs/002-rules-data-pipeline/contracts/validation-report.md` |
| `pipeline-run-interface.md` | 1.0.2 | `WargameCompanion:specs/002-rules-data-pipeline/contracts/pipeline-run-interface.md` |
| `loadout-schema-delta.md` | **1.0.0 (Frozen)** | `WargameCompanion:specs/006-unit-loadout-fidelity/contracts/loadout-schema-delta.md` |

These govern, respectively: the mapping between the curated JSON tree and the published bundle;
the validation report, finding catalogue, and resolution format; the CLI/workflow/exit-code/
configuration surface; and the additive schema delta — three new bundle arrays and four new
optional columns — `006-unit-loadout-fidelity` added on top of `curated-snapshot-format.md` and
`reference-db-schema.md` without amending either's predecessor, `bundle-schema-delta.md` v1.1.0
(`004-rules-data-enrichment`, still frozen and unamended).

`pipeline-run-interface.md` still owes two additive amendments this feature's own work created —
the `option-regression` command and the `build --published-at`/`--published-at-from-report`
options — both implemented ahead of the contract row they are owed, for the reasons
`docs/follow-ups.md` items 11 and 12 record. Neither changes what is stamped in `docs/contracts.md`
above: the contract itself is still 1.0.2 until that amendment lands.

## Stamped values

The schema and vocabulary versions above are stamped into every published snapshot's
`snapshotMeta` via the `WGC_SCHEMA_CONTRACT_VERSION` (currently `1`, the MAJOR of
`reference-db-schema.md`) and `WGC_RESTRICTION_VOCABULARY_VERSION` (currently `1`) configuration
variables (`contracts/pipeline-run-interface.md` §5).

## Changing a contract

- **This feature's own contracts** may be revised here, with a changelog entry, following the
  same discipline the frozen contracts already model.
- **The frozen consumer contracts** may only be revised in `WargameCompanion`, by agreement with
  whoever owns `001-army-builder-app`, and only ever as an additive/backward-compatible bump
  unless a breaking change is explicitly agreed and versioned as such.
