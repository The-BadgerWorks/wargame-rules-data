<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Pinned the exact contract versions this
     repository serves, per Setup task T013. -->
# Contract versions this repository serves

This repository is bound by two kinds of contract: the **frozen consumer contracts** owned by
`001-army-builder-app` (which this repository may not redefine unilaterally), and **this
feature's own contracts**, which this repository's own `contracts/` directory (mirrored from
`specs/002-rules-data-pipeline/contracts/` in `WargameCompanion`) defines.

## Frozen consumer contracts (govern)

| Contract | Version | Source of truth |
|---|---|---|
| `reference-db-schema.md` | **v1.2.0** | `WargameCompanion:specs/001-army-builder-app/contracts/reference-db-schema.md` |
| `rules-data-manifest.md` | **v1.1.1** | `WargameCompanion:specs/001-army-builder-app/contracts/rules-data-manifest.md` |

These define the JSON snapshot bundle's shape and the manifest's shape respectively. Both are
owned by `001-army-builder-app`. A change to either is a **cross-feature versioning exercise** —
coordinated with the `001` maintainers and given a new version number there — never a unilateral
edit made from this repository.

## This feature's own contracts

| Contract | Version | Source of truth |
|---|---|---|
| `curated-snapshot-format.md` | 1.0.0 | `WargameCompanion:specs/002-rules-data-pipeline/contracts/curated-snapshot-format.md` |
| `validation-report.md` | 1.0.0 | `WargameCompanion:specs/002-rules-data-pipeline/contracts/validation-report.md` |
| `pipeline-run-interface.md` | 1.0.0 | `WargameCompanion:specs/002-rules-data-pipeline/contracts/pipeline-run-interface.md` |

These govern, respectively: the mapping between the curated JSON tree and the published bundle;
the validation report, finding catalogue, and resolution format; and the CLI/workflow/exit-code/
configuration surface.

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
