<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Declared desired state for the
     repository settings that cannot be expressed as code (plan.md's documented Principle 5
     exception), plus the record of repository creation (T001) and of applying these settings
     to the live repository (T009). -->
# Repository settings: declared desired state

Per `plan.md`'s documented Principle 5 exception, three classes of GitHub repository setting
cannot be expressed as code without adding a settings-sync GitHub App (rejected as
disproportionate for a small maintainer set, Principle 14): the environments' required-reviewer
lists, branch protection on `main`, and the Pages source. This file is the reviewable source of
truth for all three. A drift-check should read them back through the API and fail on divergence
(tracked as later CI work; not part of the Setup phase).

## Repository creation (T001)

| Field | Value |
|---|---|
| Repository | `The-BadgerWorks/wargame-rules-data` |
| Template | none (empty repository) |
| Visibility | Public |
| Default branch | `main` |
| Description | "Curated, IP-stripped mechanical rules data for WargameCompanion - versioned JSON snapshots" -- factual, makes no endorsement claim (FR-050) |
| Pages URL (once enabled) | `https://the-badgerworks.github.io/wargame-rules-data/manifest.json` |

## 1. GitHub Environments

Two environments, structurally identical, differing only by the channel they gate
(`plan.md` Environment gate):

| Environment | Required reviewers | Purpose |
|---|---|---|
| `published` | `adhoxx` | Gates `publish.yml` for the **published** channel. The only code path that writes a GitHub Release and the public `site/manifest.json`. |
| `prerelease` | `adhoxx` | Gates `publish.yml` for the **pre-release** channel (`WGC_DATA_CHANNEL=prerelease`), consumed by Dev/Test app builds. |

**Known limitation (recorded precisely, not glossed over):** at the time this was written, the
`The-BadgerWorks` GitHub organization has no teams (`gh api orgs/The-BadgerWorks/teams` returns
`[]`) and the only maintainer with write access is `adhoxx`. The plan's Separation gate assumes
a distinct non-author reviewer is available for `curation/abilities/` and for approving
publication; with a single maintainer that assumption does not hold in practice. This is
recorded here as an open item rather than worked around: add a second maintainer (or a bot
account with a human behind it for review purposes) before treating the approval gate as a real
second-person control. Until then, `adhoxx` approving their own publish/candidate is the
operational reality, not the designed control.

## 2. Branch protection on `main`

| Setting | Desired value |
|---|---|
| Require a pull request before merging | yes |
| Required approving review count | 1 |
| Require review from Code Owners | yes |
| Dismiss stale approvals on new commits | yes |
| Require status checks to pass | yes -- `lint, typecheck, test` and `change-class guard` (from `.github/workflows/ci.yml`) |
| Require branches to be up to date before merging | yes |
| Require conversation resolution before merging | yes |
| Include administrators | **no**, for now -- see limitation above. With a single maintainer, enforcing this against admins would make `main` unmergeable by anyone. Revisit and flip to `yes` the day a second maintainer or reviewing bot exists. |
| Allow force pushes | no |
| Allow deletions | no |

## 3. GitHub Pages source

**Correction to the plan's stated mechanism, recorded here rather than silently reinterpreted:**
`plan.md` and `quickstart.md` describe the Pages source as "`main`, `/site`". GitHub's classic
branch-based Pages source only supports the repository root or `/docs` as the served folder --
an arbitrary path such as `/site` is not a selectable option (verified against the live
`PUT /repos/{owner}/{repo}/pages` API, which rejects a `path` other than `/` or `/docs` under
`build_type: "legacy"`). Since this repository's `docs/` is already the internal documentation
tree (not the public site), the correct mechanism is the **GitHub Actions Pages source**
(`build_type: "workflow"`): a workflow step uploads the `site/` directory as a Pages artifact
(`actions/upload-pages-artifact`) and deploys it (`actions/deploy-pages`), regardless of which
path in the repository the source files live under. This is also the natural fit for the
already-designed control flow, in which `publish.yml` and `withdraw.yml` are the only code paths
permitted to touch the live manifest (`contracts/pipeline-run-interface.md` §3-§4) -- an
Actions-based deploy step inside those gated workflows enforces that by capability, the same way
FR-052 is enforced for `candidate.yml`'s lack of a Releases/Pages-capable token.

| Setting | Desired value |
|---|---|
| Pages source | GitHub Actions (`build_type: "workflow"`) |
| Served content | `site/` (via `actions/upload-pages-artifact` in `publish.yml` / `withdraw.yml`, once those workflows exist -- Setup phase does not implement them) |
| Custom domain | none |
| Enforce HTTPS | yes |

## Applying these settings (T009)

Applied by: `adhoxx` (via `gh api`, run by an AI-assisted session -- Claude Code,
model `claude-sonnet-5`). Applied on: see the dated entries below; this file is updated each
time the live configuration changes.

| Date | Change | Result |
|---|---|---|
| 2026-08-03T13:53-13:55Z | Created `published` and `prerelease` environments, each with required reviewer `adhoxx` (`PUT /repos/The-BadgerWorks/wargame-rules-data/environments/{name}`) | Both created; `can_admins_bypass: true` (a GitHub default for environment protection, distinct from branch-protection admin enforcement) and `prevent_self_review: false` -- i.e. `adhoxx` can currently approve their own deployment to either environment, consistent with the single-maintainer limitation recorded above |
| 2026-08-03T13:53Z | Branch protection on `main`: PR required, 1 approving review, code-owner review required, dismiss stale approvals, required status checks `lint, typecheck, test` and `change-class guard` (strict), conversation resolution required, no force pushes, no deletions, `enforce_admins: false` | Applied via `PUT /repos/.../branches/main/protection`; status-check contexts confirmed against the job names of the first successful CI run (`gh run view`) before being set |
| 2026-08-03T13:55Z | Enabled GitHub Pages, `build_type: "workflow"` (GitHub Actions source, per the corrected mechanism in SS3 above) | `html_url: https://the-badgerworks.github.io/wargame-rules-data/`; `status: null` because no deploy workflow exists yet -- `publish.yml`'s `actions/deploy-pages` step (a later phase, not part of Setup) is what will populate it |

**Verification note**: `gh api orgs/The-BadgerWorks/teams` still returns `[]` at the time of
application, confirming the single-maintainer limitation stated in SS1 was not resolved before
applying these settings. `enforce_admins` was deliberately left `false` for exactly that reason
-- setting it `true` today would make `main` permanently unmergeable, since GitHub does not
allow a PR author to approve their own review requirement and no second reviewer exists.
