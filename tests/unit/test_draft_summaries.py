# AI-Assisted: Claude Code (model: claude-opus-5) - Asserts the summary drafting tool (010 R7
# task 2): it drives the Task-1 client over a build report's outstanding summary findings and
# writes CANDIDATE records to a scratch directory, never to curation/, and never lets the
# export's mechanic text reach stdout (amended standing rule 3, 2026-09-14).
# AI-Assisted: Claude Code (model: claude-opus-5) - 010 R7 task 2 fix round 1: receipts for the
# attribution pair on a redrafted re-review candidate, the build-resolved detachment id (with the
# leading-article divergence that the old slug derivation got wrong), resume/per-class writes/
# DraftingError survival, the per-record validation drop, the per-faction layout, the second
# curation-refusal, the entries-vs-calls label, and the -UNAPPROVED skip.
# AI-Assisted: Claude Code (model: claude-opus-5) - 010 R7 task 2 fix round 2: receipts for the
# key-driven detachment join (a name shared by two factions must reach BOTH curated ids), the
# ambiguous-source-id guard, a transport fault taking the partial-write path end to end, the
# recorded drafted count, and the pre-prompt resolution line.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 010 R8 task 3: receipts for `data_dir`
# being derived from the report's own run root instead of defaulting to `repository_root/data`
# (the never-guess refusal naming `--data`, the derivation from `<run root>/out/data`, the
# resolution table printing the `data_dir` it used, and the seven-detachment regression closed),
# plus `--rebaseline-authorization` as a CLI parameter over the former hard-coded citation.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 010 R8 task 3 fix round 1 (code review): a
# receipt that `_default_data_dir` does not escape the report's own run root to an unrelated
# ancestor's `out/data` (shared scratch space left over from a different run).
"""What this tool has to be trusted about is what it refuses to do.

The candidates it produces are read by the Owner and merged by hand, so the record shape is
asserted. But the tests that earn it the right to run against the live source are the refusals:
the two curation roots, the mechanic text never reaching stdout, the confirmation gate, and —
after fix round 1 — never paying twice and never discarding paid-for work.

Every string in this file is invented. `MECHANIC_*` are deliberately unmistakable: if one of
them ever appears in captured stdout, in a candidate file's `summary`, or in a diagnostic, a
test fails rather than a reviewer having to notice.
"""

from __future__ import annotations

import json
import shutil
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import pytest

from pipeline.config import ConfigError, load_config
from pipeline.exit_codes import ExitCode
from pipeline.summaries import Draft, DraftingError, Verdict
from tools.draft_summaries import (
    REBASELINE_AUTHORIZATION,
    UNASSIGNED,
    ConfirmationRefused,
    DraftRun,
    _default_data_dir,
    draft_candidates,
    main,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
MINIMAL = REPO_ROOT / "fixtures" / "minimal"

KEY = "draft-summaries-test-key"
VERSION = "wh40k-11e-2026-09-1"
DRAFT_MODEL = "invented-draft-model"
REVIEW_MODEL = "invented-review-model"
API_KEY = "unit-test-key-not-a-secret"

ENV = {
    "WGC_DETAIL_EDITION": "wh40k-11e",
    "WGC_MECHANIC_DIGEST_KEY": KEY,
    "WGC_DRAFT_MODEL": DRAFT_MODEL,
    "WGC_REVIEW_MODEL": REVIEW_MODEL,
    "WGC_ANTHROPIC_API_KEY": API_KEY,
}

# The invented mechanic text of the fixture export. Never a paraphrase of anything real.
MECHANIC_VAULT = "MECHANIC-ALPHA each time this unit invents a move, add 2 to the invented roll."
MECHANIC_CHITIN = "MECHANIC-BETA models in this unit add 1 to every invented saving throw."
MECHANIC_EMBER = "MECHANIC-GAMMA on an invented roll of 6, ignore the invented wound."
MECHANIC_CADENCE = "MECHANIC-DELTA each unit may invent one extra action in each phase."
MECHANIC_STORM = "MECHANIC-EPSILON invented ranged attacks add 1 to the invented hit roll."
MECHANIC_SHARED = "MECHANIC-ZETA invented units in this detachment reroll one invented die."
MECHANIC_CONTESTED = "MECHANIC-ETA invented charges add 1 to the invented distance."

VAULT_KEY = "datasheet:vault-cadence"
CHITIN_KEY = "faction:chitin-bloom"
EMBER_KEY = "datasheet:ember-shield"
DETACHMENT_KEY = "detachment:d-invented-vanguard:sacred-cadence"

#: The divergence receipt for fix round 1's Important 2. The points card says "The Ironstorm
#: Spearhead", so the curated id is `d-the-ironstorm-spearhead`; the CSV says "Ironstorm
#: Spearhead", so the retired `d-{slugify(csv name)}` derivation produced
#: `d-ironstorm-spearhead` — an id no curated key ever carries, which reported every rule of this
#: detachment as `unresolved`.
ARTICLE_KEY = "detachment:d-the-ironstorm-spearhead:storm-cadence"

#: Two curated ids, one shared display name, one source detachment. Both must resolve.
SHARED_KEY_ONE = "detachment:d-shared-cadre:shared-doctrine"
SHARED_KEY_TWO = "detachment:d-shared-cadre-2:shared-doctrine"

#: Reachable only through a source id that publishes two differently-named detachments.
AMBIGUOUS_KEY = "detachment:d-ambiguous-beta:contested-doctrine"

FACTION = "f-invented"

ABILITIES_CSV = f"﻿id|name|legend|faction_id|description|\nA1|Chitin Bloom||F1|{MECHANIC_CHITIN}|\n"
DATASHEETS_ABILITIES_CSV = (
    "﻿datasheet_id|line|ability_id|model|name|description|type|parameter|\n"
    f"AV01|1|||Vault Cadence|{MECHANIC_VAULT}|Datasheet||\n"
    "AV01|2|A1||||Faction||\n"
    f"AV01|3|||Ember Shield|{MECHANIC_EMBER}|Datasheet||\n"
)
DETACHMENTS_CSV = (
    "﻿id|faction_id|name|legend|type|\n"
    "D1|F1|Invented Vanguard|||\n"
    "D2|F1|Ironstorm Spearhead|||\n"
    # One name, published once, that TWO curated ids share - the chapter-duplicate shape.
    "D3|F1|Shared Cadre|||\n"
    # One source id publishing two differently-named detachments: the pipeline deletes it.
    "D4|F1|Ambiguous Alpha|||\n"
    "D4|F1|Ambiguous Beta|||\n"
)
DETACHMENT_ABILITIES_CSV = (
    "﻿id|detachment_id|name|legend|description|\n"
    f"DA1|D1|Sacred Cadence||{MECHANIC_CADENCE}|\n"
    f"DA2|D2|Storm Cadence||{MECHANIC_STORM}|\n"
    f"DA3|D3|Shared Doctrine||{MECHANIC_SHARED}|\n"
    f"DA4|D4|Contested Doctrine||{MECHANIC_CONTESTED}|\n"
)

#: The built snapshot the report came from. The detachment ids here are the ones the curated
#: `summary_key`s carry, and the tool reads them rather than re-deriving them from the CSV.
BUILT_DETACHMENTS = {
    "detachments": [
        {"detachment_id": "d-invented-vanguard", "name": "Invented Vanguard", "rules": []},
        {
            "detachment_id": "d-the-ironstorm-spearhead",
            "name": "The Ironstorm Spearhead",
            "rules": [],
        },
        # The first of two curated ids sharing one name (see BUILT_DETACHMENTS_TWO).
        {"detachment_id": "d-shared-cadre", "name": "Shared Cadre", "rules": []},
        # Reachable only through the source id the ambiguity guard deletes.
        {"detachment_id": "d-ambiguous-beta", "name": "Ambiguous Beta", "rules": []},
    ]
}

#: A second faction whose detachment carries the SAME display name as the first faction's, minted
#: `-2` by the registry exactly as the six Space Marine chapter duplicates are. Both ids must be
#: reachable: they are the per-chapter identifiers the C1 ruling exists to hold apart.
FACTION_TWO = "f-invented-two"
BUILT_DETACHMENTS_TWO = {
    "detachments": [
        {"detachment_id": "d-shared-cadre-2", "name": "Shared Cadre", "rules": []},
    ]
}


# --------------------------------------------------------------------------------------
# The fake client. No HTTP anywhere — not even a mock transport.
# --------------------------------------------------------------------------------------


@dataclass
class FakeClient:
    """Stands in for :class:`pipeline.summaries.SummaryClient`, recording every call.

    Scripted per *name* rather than per key, because that is all the client is ever handed: a
    client that could see a key would be a client that could be scripted on something the real
    one cannot observe.
    """

    drafts: dict[str, list[Draft]] = field(default_factory=dict)
    verdicts: dict[str, list[Verdict]] = field(default_factory=dict)
    default_draft: Draft = Draft("An invented candidate summary.", False)
    default_verdict: Verdict = Verdict("keep", "ok")
    raise_on_draft: dict[str, DraftingError] = field(default_factory=dict)
    draft_calls: list[tuple[str, str, str, str | None]] = field(default_factory=list)
    review_calls: list[tuple[str, str, str]] = field(default_factory=list)

    def draft(
        self,
        name: str,
        mechanic_text: str,
        *,
        ability_class: Literal["ability", "detachment_rule"],
        hint: str | None = None,
    ) -> Draft:
        self.draft_calls.append((name, mechanic_text, ability_class, hint))
        failure = self.raise_on_draft.get(name)
        if failure is not None:
            raise failure
        queue = self.drafts.get(name)
        if queue:
            return queue.pop(0)
        return self.default_draft

    def review(self, name: str, mechanic_text: str, summary: str) -> Verdict:
        self.review_calls.append((name, mechanic_text, summary))
        queue = self.verdicts.get(name)
        if queue:
            return queue.pop(0)
        return self.default_verdict


class ExplodingClient:
    """Any call at all is the failure this client exists to detect."""

    def draft(self, *args: Any, **kwargs: Any) -> Draft:
        raise AssertionError("draft() was called when no call should have been made")

    def review(self, *args: Any, **kwargs: Any) -> Verdict:
        raise AssertionError("review() was called when no call should have been made")


# --------------------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------------------


@pytest.fixture
def fixtures_dir(tmp_path: Path) -> Path:
    """A copy of the minimal fixture set with the four tables this tool reads rewritten.

    Copied rather than built from nothing so that every table the acquisition asserts the
    presence of is present (trap 9), while the rows this tool actually joins are ours.
    """
    root = tmp_path / "fixtures"
    shutil.copytree(MINIMAL, root)
    wahapedia = root / "wahapedia"
    (wahapedia / "Abilities.csv").write_text(ABILITIES_CSV, encoding="utf-8", newline="")
    (wahapedia / "Datasheets_abilities.csv").write_text(
        DATASHEETS_ABILITIES_CSV, encoding="utf-8", newline=""
    )
    (wahapedia / "Detachments.csv").write_text(DETACHMENTS_CSV, encoding="utf-8", newline="")
    (wahapedia / "Detachment_abilities.csv").write_text(
        DETACHMENT_ABILITIES_CSV, encoding="utf-8", newline=""
    )
    return root


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A stand-in repository root: `work/`, a `curation/` it may not write, and a built `data/`."""
    root = tmp_path / "repo"
    (root / "work").mkdir(parents=True)
    (root / "curation" / "abilities").mkdir(parents=True)
    (root / "curation" / "detachment-rules").mkdir(parents=True)
    built = root / "data" / "wh40k-11e" / "factions" / FACTION
    built.mkdir(parents=True)
    (built / "detachments.json").write_text(json.dumps(BUILT_DETACHMENTS), encoding="utf-8")
    built_two = root / "data" / "wh40k-11e" / "factions" / FACTION_TWO
    built_two.mkdir(parents=True)
    (built_two / "detachments.json").write_text(json.dumps(BUILT_DETACHMENTS_TWO), encoding="utf-8")
    return root


def write_report(path: Path, findings: Sequence[dict[str, Any]]) -> Path:
    path.write_text(json.dumps({"findings": list(findings)}), encoding="utf-8")
    return path


def finding(code: str, key: str, *, key_field: str = "ability_key") -> dict[str, Any]:
    return {"finding_code": code, "entity_refs": [key], "detail": {key_field: key}}


def authored(repo: Path, relative: str, records: Sequence[dict[str, Any]]) -> None:
    path = repo / "curation" / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(list(records), indent=2), encoding="utf-8")


def approved_ability(key: str, name: str, summary: str, digest: str = "0" * 32) -> dict[str, Any]:
    return {
        "ability_key": key,
        "name": name,
        "summary": summary,
        "review_state": "approved",
        "mechanic_digest": digest,
        "reviewed_by": "someone-else",
        "reviewed_at": "2026-01-01T00:00:00Z",
    }


def run(
    repo: Path,
    fixtures_dir: Path,
    report: Path,
    out: Path,
    *,
    drafter: Any,
    reviewer: Any,
    classes: Sequence[str] = ("abilities",),
    limit: int | None = None,
    assume_yes: bool = True,
    transport: str = "api",
) -> DraftRun:
    from pipeline.config import load_config

    return draft_candidates(
        load_config(env=ENV),
        transport=transport,
        repository_root=repo,
        report_path=report,
        out_dir=out,
        version=VERSION,
        classes=classes,
        drafter=drafter,
        reviewer=reviewer,
        fixtures_dir=fixtures_dir,
        offline=True,
        limit=limit,
        assume_yes=assume_yes,
        # 010 R8 task 3: every test using this helper writes its `report.json` loose under
        # `tmp_path`, with no `<run root>/out/data` anywhere above it, so the tool's new
        # never-guess default would refuse with a ConfigError. Naming the `repo` fixture's own
        # built tree here is this helper's business, not the tool's default — the default itself
        # is asserted separately, against a report placed where a real build would leave it.
        data_dir=repo / "data",
    )


def records(out: Path, relative: str) -> list[dict[str, Any]]:
    return json.loads((out / relative).read_text(encoding="utf-8"))


def expected_digests(fixtures_dir: Path) -> dict[str, str]:
    from pipeline.acquire.detail_source import acquire_detail, read_detail
    from pipeline.config import load_config
    from pipeline.curate.summaries import compute_current_digests

    config = load_config(env=ENV)
    _acq, payloads = acquire_detail(config, fixtures_dir=fixtures_dir, offline=True)
    return compute_current_digests(read_detail(payloads), key=KEY.encode("utf-8"))


# --------------------------------------------------------------------------------------
# (a) a missing ability key becomes one candidate, digested from the current source
# --------------------------------------------------------------------------------------


def test_a_missing_ability_key_yields_one_candidate_with_the_current_digest(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    report = write_report(tmp_path / "report.json", [finding("SUM-MISSING", VAULT_KEY)])
    client = FakeClient(drafts={"Vault Cadence": [Draft("An invented mechanic summary.", False)]})
    out = tmp_path / "candidates"

    outcome = run(repo, fixtures_dir, report, out, drafter=client, reviewer=client)

    written = records(out, f"abilities/{UNASSIGNED}.json")
    assert [record["ability_key"] for record in written] == [VAULT_KEY]
    assert written[0]["mechanic_digest"] == expected_digests(fixtures_dir)[VAULT_KEY]
    assert written[0]["review_state"] == "approved"
    assert written[0]["reviewed_by"] == f"{REVIEW_MODEL}-reviewer"
    assert written[0]["summary"] == "An invented mechanic summary."
    assert written[0]["authored_against_acquisition"]
    assert outcome.by_class["abilities"].kept == (VAULT_KEY,)


def test_a_key_with_no_curated_record_carries_no_attribution_pair(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    """The pair says "an approval was carried across a digest move". A new key carries none."""
    report = write_report(tmp_path / "report.json", [finding("SUM-MISSING", VAULT_KEY)])
    out = tmp_path / "out"

    run(repo, fixtures_dir, report, out, drafter=FakeClient(), reviewer=FakeClient())

    record = records(out, f"abilities/{UNASSIGNED}.json")[0]
    assert "digest_refreshed_at_version" not in record
    assert "digest_refreshed_under_authorization" not in record


def test_the_client_is_asked_for_a_draft_then_a_review(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    report = write_report(tmp_path / "report.json", [finding("SUM-MISSING", VAULT_KEY)])
    client = FakeClient()

    run(repo, fixtures_dir, report, tmp_path / "out", drafter=client, reviewer=client)

    assert [call[0] for call in client.draft_calls] == ["Vault Cadence"]
    assert client.draft_calls[0][2] == "ability"
    assert client.draft_calls[0][3] is None, "a first attempt carries no redraft hint"
    assert [call[0] for call in client.review_calls] == ["Vault Cadence"]


# --------------------------------------------------------------------------------------
# (b) a re-review key the reviewer keeps becomes a re-baseline candidate
# --------------------------------------------------------------------------------------


def test_a_kept_rereview_key_yields_a_rebaseline_candidate_with_both_attribution_fields(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    authored(
        repo,
        f"abilities/{FACTION}.json",
        [approved_ability(EMBER_KEY, "Ember Shield", "An invented summary a curator approved.")],
    )
    report = write_report(tmp_path / "report.json", [finding("SUM-NEEDS-REREVIEW", EMBER_KEY)])
    client = FakeClient()
    out = tmp_path / "candidates"

    outcome = run(repo, fixtures_dir, report, out, drafter=client, reviewer=client)

    # The re-baseline lands in the faction file the curated record came from, not in unassigned.
    written = records(out, f"abilities/{FACTION}.json")
    assert [record["ability_key"] for record in written] == [EMBER_KEY]
    record = written[0]
    # The NEW digest, not the stale one the curated record was approved against.
    assert record["mechanic_digest"] == expected_digests(fixtures_dir)[EMBER_KEY]
    assert record["mechanic_digest"] != "0" * 32
    assert record["digest_refreshed_at_version"] == VERSION
    assert record["digest_refreshed_under_authorization"] == REBASELINE_AUTHORIZATION
    # The approved summary is carried across unchanged; the reviewer said keep, not redraft.
    assert record["summary"] == "An invented summary a curator approved."
    assert client.draft_calls == []
    assert outcome.by_class["abilities"].rebaselined == (EMBER_KEY,)


def test_the_blanket_authorization_is_the_key_rotation_ruling() -> None:
    assert REBASELINE_AUTHORIZATION == "owner-2026-09-15-digest-key-rotation"


def test_the_superseded_authorization_string_appears_nowhere_in_the_tool() -> None:
    """Ruling 6 supersedes ruling 3, and the superseded string must appear nowhere.

    Assembled from fragments rather than written out, because "nowhere" includes this file.
    """
    superseded = "-".join(("owner", "2026", "09", "14", "csv", "cutover", "rebaseline"))
    source = (REPO_ROOT / "tools" / "draft_summaries.py").read_text(encoding="utf-8")
    assert superseded not in source
    assert superseded != REBASELINE_AUTHORIZATION


# --------------------------------------------------------------------------------------
# (c) a re-review key the reviewer rejects is drafted fresh — Important 1
# --------------------------------------------------------------------------------------


def test_a_redrafted_rereview_candidate_still_carries_the_attribution_pair(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    """Fix round 1, Important 1 — the receipt.

    `tools/check_summary_approvals.py`'s `digest_refreshes` reads `carries_approval` from the
    base and head `review_state` ALONE. The curated record is `approved` at base; the merged
    candidate is `approved` at head; the digest moved. That is a carried approval as far as the
    guard is concerned, however this tool got the summary, so the pair must be present or
    `cmd_diff` returns 1 on the Owner's merge PR. Remove the `prior.get("review_state") ==
    "approved"` branch in `_work_one` and this test fails on the first assertion.
    """
    authored(
        repo,
        f"abilities/{FACTION}.json",
        [approved_ability(EMBER_KEY, "Ember Shield", "An invented summary that no longer fits.")],
    )
    report = write_report(tmp_path / "report.json", [finding("SUM-NEEDS-REREVIEW", EMBER_KEY)])
    client = FakeClient(
        verdicts={"Ember Shield": [Verdict("redraft", "meaning-changed"), Verdict("keep", "ok")]},
        drafts={"Ember Shield": [Draft("A freshly invented summary.", False)]},
    )
    out = tmp_path / "candidates"

    outcome = run(repo, fixtures_dir, report, out, drafter=client, reviewer=client)

    record = records(out, f"abilities/{FACTION}.json")[0]
    assert record["digest_refreshed_at_version"] == VERSION
    assert record["digest_refreshed_under_authorization"] == REBASELINE_AUTHORIZATION
    assert record["summary"] == "A freshly invented summary."
    assert [call[0] for call in client.draft_calls] == ["Ember Shield"]
    assert outcome.by_class["abilities"].kept == (EMBER_KEY,)
    assert outcome.by_class["abilities"].rebaselined == ()


def test_the_guard_accepts_a_redrafted_rereview_candidate_merged_into_curation(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    """The same finding, asserted against the guard itself rather than against our reading of it.

    Simulates the Owner's merge: base is the committed curated file, head is that file with the
    candidate's record in place of it, and the guard is asked whether the refresh is attributed.
    """
    from tools.check_summary_approvals import digest_refreshes, unattributed_refreshes

    base = [approved_ability(EMBER_KEY, "Ember Shield", "An invented summary that no longer fits.")]
    authored(repo, f"abilities/{FACTION}.json", base)
    report = write_report(tmp_path / "report.json", [finding("SUM-NEEDS-REREVIEW", EMBER_KEY)])
    client = FakeClient(
        verdicts={"Ember Shield": [Verdict("redraft", "meaning-changed"), Verdict("keep", "ok")]}
    )
    out = tmp_path / "candidates"
    run(repo, fixtures_dir, report, out, drafter=client, reviewer=client)

    head = records(out, f"abilities/{FACTION}.json")
    assert unattributed_refreshes(digest_refreshes(base, head)) == []
    # …and the guard really does see a refresh here, so the assertion above is not vacuous.
    assert [refresh.key for refresh in digest_refreshes(base, head)] == [EMBER_KEY]


def test_a_redraft_verdict_on_a_fresh_draft_costs_one_more_draft_and_review(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    report = write_report(tmp_path / "report.json", [finding("SUM-MISSING", VAULT_KEY)])
    client = FakeClient(
        verdicts={"Vault Cadence": [Verdict("redraft", "too-long"), Verdict("keep", "ok")]},
        drafts={
            "Vault Cadence": [Draft("First invented attempt.", False), Draft("Second try.", False)]
        },
    )
    out = tmp_path / "candidates"

    outcome = run(repo, fixtures_dir, report, out, drafter=client, reviewer=client)

    assert len(client.draft_calls) == 2
    assert len(client.review_calls) == 2
    assert records(out, f"abilities/{UNASSIGNED}.json")[0]["summary"] == "Second try."
    assert outcome.by_class["abilities"].redrafted == (VAULT_KEY,)


def test_the_redraft_carries_the_reviewers_reason_code_as_a_hint(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    """The plan's "one more draft WITH the reason code", now that `draft` has a `hint`."""
    report = write_report(tmp_path / "report.json", [finding("SUM-MISSING", VAULT_KEY)])
    client = FakeClient(
        verdicts={"Vault Cadence": [Verdict("redraft", "meaning-changed"), Verdict("keep", "ok")]}
    )

    run(repo, fixtures_dir, report, tmp_path / "out", drafter=client, reviewer=client)

    assert [call[3] for call in client.draft_calls] == [None, "meaning-changed"]


# --------------------------------------------------------------------------------------
# (d) two lore verdicts drop the key and list it
# --------------------------------------------------------------------------------------


def test_two_lore_verdicts_drop_the_key_and_list_it(
    repo: Path, fixtures_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    report = write_report(tmp_path / "report.json", [finding("SUM-MISSING", VAULT_KEY)])
    client = FakeClient(
        verdicts={
            "Vault Cadence": [Verdict("lore", "lore-present"), Verdict("lore", "lore-present")]
        }
    )
    out = tmp_path / "candidates"

    outcome = run(repo, fixtures_dir, report, out, drafter=client, reviewer=client)

    assert outcome.by_class["abilities"].dropped_lore == (VAULT_KEY,)
    assert outcome.by_class["abilities"].kept == ()
    assert not (out / "abilities").exists()
    printed = capsys.readouterr().out
    assert VAULT_KEY in printed
    assert "dropped" in printed


# --------------------------------------------------------------------------------------
# (e) the tool refuses an --out inside curation/ — including the REAL repository's
# --------------------------------------------------------------------------------------


def _refusal_argv(repo: Path, fixtures_dir: Path, report: Path, out: Path) -> list[str]:
    return [
        "--report", str(report),
        "--out", str(out),
        "--version", VERSION,
        "--repo", str(repo),
        # 010 R8 task 3: every caller of this helper writes `report.json` loose under
        # `tmp_path`, with no `<run root>/out/data` above it, so the tool's new never-guess
        # default would refuse with a ConfigError. `--data` names the `repo` fixture's own
        # built tree explicitly, exactly as a real caller must once the report and the build
        # it came from are not siblings on disk.
        "--data", str(repo / "data"),
        "--fixtures", str(fixtures_dir),
        "--offline",
        "--yes",
    ]  # fmt: skip


def test_it_refuses_an_out_directory_inside_the_repository_curation_tree(
    repo: Path, fixtures_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    report = write_report(tmp_path / "report.json", [finding("SUM-MISSING", VAULT_KEY)])
    out = repo / "curation" / "abilities" / "candidates"

    code = main(_refusal_argv(repo, fixtures_dir, report, out), env=ENV, clients=None)

    # Also assert WHY: an unset API key would otherwise exit 60 too, and this test would pass
    # with the refusal deleted.
    assert code == 60
    assert "curation" in capsys.readouterr().err


def test_it_refuses_an_out_directory_that_reaches_curation_through_a_relative_path(
    repo: Path, fixtures_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    report = write_report(tmp_path / "report.json", [finding("SUM-MISSING", VAULT_KEY)])
    out = repo / "work" / ".." / "curation" / "sneaky"

    code = main(_refusal_argv(repo, fixtures_dir, report, out), env=ENV)

    assert code == 60
    assert "curation" in capsys.readouterr().err


def test_it_refuses_curation_itself(
    repo: Path, fixtures_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    report = write_report(tmp_path / "report.json", [finding("SUM-MISSING", VAULT_KEY)])

    code = main(_refusal_argv(repo, fixtures_dir, report, repo / "curation"), env=ENV)

    assert code == 60
    assert "curation" in capsys.readouterr().err


def test_it_refuses_the_real_checkouts_curation_even_when_repo_points_elsewhere(
    repo: Path, fixtures_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Fix round 1, minor 6 — `--repo` is an argument, and an argument can be wrong.

    `--repo <tmp> --out <this checkout>/curation/...` passed the single-root check while writing
    straight into the tree the tool exists to keep out of.
    """
    report = write_report(tmp_path / "report.json", [finding("SUM-MISSING", VAULT_KEY)])
    out = REPO_ROOT / "curation" / "abilities" / "never-written"

    code = main(_refusal_argv(repo, fixtures_dir, report, out), env=ENV)

    assert code == 60
    assert "curation" in capsys.readouterr().err
    assert not out.exists(), "the refusal must happen before anything is created"


def test_nothing_is_written_under_curation(repo: Path, fixtures_dir: Path, tmp_path: Path) -> None:
    before = sorted(p.relative_to(repo) for p in (repo / "curation").rglob("*"))
    report = write_report(tmp_path / "report.json", [finding("SUM-MISSING", VAULT_KEY)])
    run(repo, fixtures_dir, report, tmp_path / "out", drafter=FakeClient(), reviewer=FakeClient())
    after = sorted(p.relative_to(repo) for p in (repo / "curation").rglob("*"))
    assert before == after


# --------------------------------------------------------------------------------------
# (f) the export's mechanic text never reaches stdout
# --------------------------------------------------------------------------------------


ALL_MECHANICS = (
    MECHANIC_VAULT,
    MECHANIC_CHITIN,
    MECHANIC_EMBER,
    MECHANIC_CADENCE,
    MECHANIC_STORM,
    MECHANIC_SHARED,
    MECHANIC_CONTESTED,
)


def test_the_mechanic_text_never_reaches_stdout(
    repo: Path, fixtures_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    report = write_report(
        tmp_path / "report.json",
        [
            finding("SUM-MISSING", VAULT_KEY),
            finding("SUM-MISSING", CHITIN_KEY),
            finding("DRL-OUTSTANDING", DETACHMENT_KEY, key_field="summary_key"),
        ],
    )
    run(
        repo,
        fixtures_dir,
        report,
        tmp_path / "out",
        drafter=FakeClient(),
        reviewer=FakeClient(),
        classes=("abilities", "detachment_rules"),
    )
    captured = capsys.readouterr()
    for text in ALL_MECHANICS:
        assert text not in captured.out
        assert text not in captured.err
    # And the keys, which are what the tool exists to report, DO reach it.
    assert VAULT_KEY in captured.out
    assert DETACHMENT_KEY in captured.out


def test_the_digest_key_never_reaches_stdout(
    repo: Path, fixtures_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    report = write_report(tmp_path / "report.json", [finding("SUM-MISSING", VAULT_KEY)])
    run(repo, fixtures_dir, report, tmp_path / "out", drafter=FakeClient(), reviewer=FakeClient())
    captured = capsys.readouterr()
    assert KEY not in captured.out
    assert KEY not in captured.err


# --------------------------------------------------------------------------------------
# --limit, and the confirmation gate
# --------------------------------------------------------------------------------------


def test_limit_caps_the_number_of_keys_worked(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    report = write_report(
        tmp_path / "report.json",
        [
            finding("SUM-MISSING", VAULT_KEY),
            finding("SUM-MISSING", CHITIN_KEY),
            finding("SUM-MISSING", EMBER_KEY),
        ],
    )
    client = FakeClient()
    out = tmp_path / "out"

    outcome = run(repo, fixtures_dir, report, out, drafter=client, reviewer=client, limit=2)

    assert len(records(out, f"abilities/{UNASSIGNED}.json")) == 2
    assert len(client.draft_calls) == 2
    # Worked in sorted key order, so the last key alphabetically is the one left over.
    assert outcome.by_class["abilities"].skipped_over_limit == (CHITIN_KEY,)


def test_without_yes_and_non_interactive_it_refuses_before_any_api_call(
    repo: Path, fixtures_dir: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("tools.draft_summaries.sys.stdin", _NonInteractiveStdin())
    report = write_report(tmp_path / "report.json", [finding("SUM-MISSING", VAULT_KEY)])
    out = tmp_path / "out"

    with pytest.raises(ConfirmationRefused):
        run(
            repo,
            fixtures_dir,
            report,
            out,
            drafter=ExplodingClient(),
            reviewer=ExplodingClient(),
            assume_yes=False,
        )
    assert not out.exists()


def test_yes_proceeds_without_a_prompt(
    repo: Path, fixtures_dir: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("tools.draft_summaries.sys.stdin", _NonInteractiveStdin())
    report = write_report(tmp_path / "report.json", [finding("SUM-MISSING", VAULT_KEY)])

    outcome = run(
        repo,
        fixtures_dir,
        report,
        tmp_path / "out",
        drafter=FakeClient(),
        reviewer=FakeClient(),
        assume_yes=True,
    )
    assert outcome.by_class["abilities"].kept == (VAULT_KEY,)


def test_the_estimate_is_printed_before_the_first_call(
    repo: Path, fixtures_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    report = write_report(
        tmp_path / "report.json",
        [finding("SUM-MISSING", VAULT_KEY), finding("SUM-MISSING", CHITIN_KEY)],
    )
    run(repo, fixtures_dir, report, tmp_path / "out", drafter=FakeClient(), reviewer=FakeClient())
    printed = capsys.readouterr().out
    # Two entries, two calls each before any redraft.
    assert "4 API calls" in printed
    assert "tokens" in printed


class _NonInteractiveStdin:
    def isatty(self) -> bool:
        return False

    def readline(self) -> str:  # pragma: no cover - never reached; isatty gates it
        raise AssertionError("a non-interactive run must not read stdin")


# --------------------------------------------------------------------------------------
# The detachment-rule class, and the build-resolved id — Important 2
# --------------------------------------------------------------------------------------


def test_a_detachment_rule_finding_yields_a_candidate_in_its_own_faction_file(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    report = write_report(
        tmp_path / "report.json",
        [finding("DRL-OUTSTANDING", DETACHMENT_KEY, key_field="summary_key")],
    )
    client = FakeClient()
    out = tmp_path / "out"

    run(
        repo, fixtures_dir, report, out, drafter=client, reviewer=client,
        classes=("detachment_rules",),
    )  # fmt: skip

    # The faction comes from the built snapshot's own directory, not from a guess.
    written = records(out, f"detachment-rules/{FACTION}.json")
    assert [record["summary_key"] for record in written] == [DETACHMENT_KEY]
    assert written[0]["detachment_id"] == "d-invented-vanguard"
    assert written[0]["name"] == "Sacred Cadence"
    assert client.draft_calls[0][2] == "detachment_rule"
    assert not (out / "abilities").exists()


def test_a_detachment_whose_card_name_carries_an_article_still_resolves(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    """Fix round 1, Important 2 — the receipt.

    The built snapshot names the detachment "The Ironstorm Spearhead", so its curated id is
    `d-the-ironstorm-spearhead`. The CSV names it "Ironstorm Spearhead". The retired derivation
    `d-{slugify(csv name)}` produced `d-ironstorm-spearhead`, which matches no curated key, so
    every rule of this detachment was reported `unresolved` — indistinguishable from a genuinely
    unpublished key. Restore that derivation and this test fails: the key goes to `unresolved`
    and no candidate is written.
    """
    report = write_report(
        tmp_path / "report.json", [finding("DRL-OUTSTANDING", ARTICLE_KEY, key_field="summary_key")]
    )
    out = tmp_path / "out"

    outcome = run(
        repo, fixtures_dir, report, out, drafter=FakeClient(), reviewer=FakeClient(),
        classes=("detachment_rules",),
    )  # fmt: skip

    assert outcome.by_class["detachment_rules"].unresolved == ()
    assert outcome.by_class["detachment_rules"].kept == (ARTICLE_KEY,)
    written = records(out, f"detachment-rules/{FACTION}.json")
    assert [record["summary_key"] for record in written] == [ARTICLE_KEY]
    assert written[0]["detachment_id"] == "d-the-ironstorm-spearhead"


def test_a_detachment_the_build_does_not_carry_is_unresolved_not_invented(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    key = "detachment:d-not-in-this-build:storm-cadence"
    report = write_report(
        tmp_path / "report.json", [finding("DRL-OUTSTANDING", key, key_field="summary_key")]
    )
    client = FakeClient()

    outcome = run(
        repo, fixtures_dir, report, tmp_path / "out", drafter=client, reviewer=client,
        classes=("detachment_rules",),
    )  # fmt: skip

    assert outcome.by_class["detachment_rules"].unresolved == (key,)
    assert client.draft_calls == []


# --------------------------------------------------------------------------------------
# Cost control — Important 3
# --------------------------------------------------------------------------------------


def test_a_second_invocation_never_pays_for_a_key_the_first_already_drafted(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    """Fix round 1, Important 3(a) — the receipt. One budget, one billing per key."""
    report = write_report(tmp_path / "report.json", [finding("SUM-MISSING", VAULT_KEY)])
    out = tmp_path / "out"
    first = FakeClient()
    run(repo, fixtures_dir, report, out, drafter=first, reviewer=first)
    assert len(first.draft_calls) == 1

    second = ExplodingClient()
    outcome = run(repo, fixtures_dir, report, out, drafter=second, reviewer=second)

    assert outcome.by_class["abilities"].already_drafted == (VAULT_KEY,)
    assert outcome.by_class["abilities"].kept == ()
    assert len(records(out, f"abilities/{UNASSIGNED}.json")) == 1


def test_a_resumed_run_extends_the_file_rather_than_replacing_it(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    out = tmp_path / "out"
    first = write_report(tmp_path / "first.json", [finding("SUM-MISSING", VAULT_KEY)])
    run(repo, fixtures_dir, first, out, drafter=FakeClient(), reviewer=FakeClient())

    second = write_report(
        tmp_path / "second.json",
        [finding("SUM-MISSING", VAULT_KEY), finding("SUM-MISSING", CHITIN_KEY)],
    )
    client = FakeClient()
    run(repo, fixtures_dir, second, out, drafter=client, reviewer=client)

    written = records(out, f"abilities/{UNASSIGNED}.json")
    assert sorted(record["ability_key"] for record in written) == sorted([VAULT_KEY, CHITIN_KEY])
    assert [call[0] for call in client.draft_calls] == ["Chitin Bloom"], "only the new key is paid"


def test_limit_plus_resume_works_the_next_slice_rather_than_the_same_one(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    report = write_report(
        tmp_path / "report.json",
        [
            finding("SUM-MISSING", VAULT_KEY),
            finding("SUM-MISSING", CHITIN_KEY),
            finding("SUM-MISSING", EMBER_KEY),
        ],
    )
    out = tmp_path / "out"
    first = FakeClient()
    run(repo, fixtures_dir, report, out, drafter=first, reviewer=first, limit=2)
    second = FakeClient()
    run(repo, fixtures_dir, report, out, drafter=second, reviewer=second, limit=2)

    assert len(second.draft_calls) == 1, "the third key, not the first two again"
    assert len(records(out, f"abilities/{UNASSIGNED}.json")) == 3


def test_a_drafting_error_keeps_every_candidate_produced_before_it(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    """Fix round 1, Important 3(b)+(c) — the receipt.

    The bill for everything before the failure is already paid. Before the fix, `_write` ran only
    after the whole `with workspace(...)` block, so an uncaught `DraftingError` discarded every
    candidate in the run.
    """
    report = write_report(
        tmp_path / "report.json",
        [
            finding("SUM-MISSING", EMBER_KEY),
            finding("SUM-MISSING", VAULT_KEY),
            finding("SUM-MISSING", CHITIN_KEY),
        ],
    )
    out = tmp_path / "out"
    # Sorted order is ember, vault, chitin — so the second key is where it stops.
    client = FakeClient(raise_on_draft={"Vault Cadence": DraftingError(400)})

    outcome = run(repo, fixtures_dir, report, out, drafter=client, reviewer=client)

    assert outcome.failure is not None
    assert VAULT_KEY in outcome.failure
    assert outcome.by_class["abilities"].kept == (EMBER_KEY,)
    assert outcome.by_class["abilities"].not_attempted == (CHITIN_KEY,)
    assert [r["ability_key"] for r in records(out, f"abilities/{UNASSIGNED}.json")] == [EMBER_KEY]


def test_the_failure_message_never_carries_a_reply_body(
    repo: Path, fixtures_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    report = write_report(tmp_path / "report.json", [finding("SUM-MISSING", VAULT_KEY)])
    client = FakeClient(raise_on_draft={"Vault Cadence": DraftingError(None)})

    outcome = run(repo, fixtures_dir, report, tmp_path / "out", drafter=client, reviewer=client)

    captured = capsys.readouterr()
    assert outcome.failure is not None
    for text in ALL_MECHANICS:
        assert text not in str(outcome.failure)
        assert text not in captured.out


def test_an_incomplete_run_exits_non_zero(repo: Path, fixtures_dir: Path, tmp_path: Path) -> None:
    """A run that stopped early must not report success — a green check over work not done."""
    report = write_report(tmp_path / "report.json", [finding("SUM-MISSING", VAULT_KEY)])
    client = FakeClient(raise_on_draft={"Vault Cadence": DraftingError(529)})

    code = main(
        _refusal_argv(repo, fixtures_dir, report, tmp_path / "out"),
        env=ENV,
        clients=(client, client),
    )

    assert code != 0


def test_a_complete_run_exits_zero(repo: Path, fixtures_dir: Path, tmp_path: Path) -> None:
    report = write_report(tmp_path / "report.json", [finding("SUM-MISSING", VAULT_KEY)])
    client = FakeClient()

    code = main(
        _refusal_argv(repo, fixtures_dir, report, tmp_path / "out"),
        env=ENV,
        clients=(client, client),
    )

    assert code == 0


def test_a_failure_in_the_first_class_does_not_discard_it_or_start_the_second(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    report = write_report(
        tmp_path / "report.json",
        [
            finding("SUM-MISSING", EMBER_KEY),
            finding("SUM-MISSING", VAULT_KEY),
            finding("DRL-OUTSTANDING", DETACHMENT_KEY, key_field="summary_key"),
        ],
    )
    out = tmp_path / "out"
    client = FakeClient(raise_on_draft={"Vault Cadence": DraftingError(529)})

    outcome = run(
        repo, fixtures_dir, report, out, drafter=client, reviewer=client,
        classes=("abilities", "detachment_rules"),
    )  # fmt: skip

    assert [r["ability_key"] for r in records(out, f"abilities/{UNASSIGNED}.json")] == [EMBER_KEY]
    assert not (out / "detachment-rules").exists()
    assert outcome.by_class["detachment_rules"].not_attempted == (DETACHMENT_KEY,)


def test_an_unexpected_fault_in_the_second_class_keeps_the_first_classs_file(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    """Fix round 1, Important 3(b) — the receipt, and the one case (c) alone does not cover.

    `DraftingError` is caught per key. Anything else is not, and must not be: an unexpected fault
    is a bug, and swallowing it would hide it. What must survive it is the money already spent.
    Defer `_write` to after the `with workspace(...)` block, as before the fix, and the exception
    leaves the function before anything is written — the first class's paid-for candidates go
    with it.
    """
    report = write_report(
        tmp_path / "report.json",
        [
            finding("SUM-MISSING", VAULT_KEY),
            finding("DRL-OUTSTANDING", DETACHMENT_KEY, key_field="summary_key"),
        ],
    )
    out = tmp_path / "out"
    drafter = FakeClient()

    class _Reviewer:
        calls = 0

        def review(self, name: str, mechanic_text: str, summary: str) -> Verdict:
            _Reviewer.calls += 1
            if name == "Sacred Cadence":
                raise RuntimeError("an invented unexpected fault")
            return Verdict("keep", "ok")

    with pytest.raises(RuntimeError):
        run(
            repo, fixtures_dir, report, out, drafter=drafter, reviewer=_Reviewer(),
            classes=("abilities", "detachment_rules"),
        )  # fmt: skip

    assert [r["ability_key"] for r in records(out, f"abilities/{UNASSIGNED}.json")] == [VAULT_KEY]


# --------------------------------------------------------------------------------------
# Fix round 2 — A: one detachment name, two curated ids, both reachable
# --------------------------------------------------------------------------------------


def test_a_detachment_name_two_factions_share_resolves_to_both_curated_ids(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    """Fix round 2, Important A — the receipt.

    The source publishes "Shared Cadre" once; two curated ids carry that name, one per faction,
    minted `-2` by the registry exactly as the six Space Marine chapter duplicates are. A
    source-driven, one-to-one join (`setdefault`, or last-write-wins) reaches exactly one of them
    and silently drops the other — measured at 78 of 346 detachment ids and 68 of 324 rules in the
    live tree. Restore that join and this test fails: one key becomes `unresolved` and its
    faction file is never written.
    """
    report = write_report(
        tmp_path / "report.json",
        [
            finding("DRL-OUTSTANDING", SHARED_KEY_ONE, key_field="summary_key"),
            finding("DRL-OUTSTANDING", SHARED_KEY_TWO, key_field="summary_key"),
        ],
    )
    out = tmp_path / "out"

    outcome = run(
        repo, fixtures_dir, report, out, drafter=FakeClient(), reviewer=FakeClient(),
        classes=("detachment_rules",),
    )  # fmt: skip

    assert outcome.by_class["detachment_rules"].unresolved == ()
    assert sorted(outcome.by_class["detachment_rules"].kept) == sorted(
        [SHARED_KEY_ONE, SHARED_KEY_TWO]
    )
    # Each chapter's key lands in its OWN faction file, which is the point of holding them apart.
    first = records(out, f"detachment-rules/{FACTION}.json")
    second = records(out, f"detachment-rules/{FACTION_TWO}.json")
    assert [record["summary_key"] for record in first] == [SHARED_KEY_ONE]
    assert [record["summary_key"] for record in second] == [SHARED_KEY_TWO]
    assert first[0]["detachment_id"] == "d-shared-cadre"
    assert second[0]["detachment_id"] == "d-shared-cadre-2"
    # Same source rule, so the same mechanic — and so the same digest — under two keys.
    assert first[0]["mechanic_digest"] == second[0]["mechanic_digest"]


def test_a_key_whose_slug_matches_no_rule_of_its_detachment_is_unresolved(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    """The key names the detachment AND the rule; a wrong rule slug must not fall back."""
    key = "detachment:d-invented-vanguard:no-such-rule"
    report = write_report(
        tmp_path / "report.json", [finding("DRL-OUTSTANDING", key, key_field="summary_key")]
    )
    client = FakeClient()

    outcome = run(
        repo, fixtures_dir, report, tmp_path / "out", drafter=client, reviewer=client,
        classes=("detachment_rules",),
    )  # fmt: skip

    assert outcome.by_class["detachment_rules"].unresolved == (key,)
    assert client.draft_calls == []


# --------------------------------------------------------------------------------------
# Fix round 2 — C: the ambiguous source id is dropped, not resolved to the last row
# --------------------------------------------------------------------------------------


def test_a_source_id_publishing_two_names_yields_nothing_rather_than_a_guess(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    """Fix round 2, minor C — the receipt, and the one failure mode that mis-attributes.

    Source id `D4` publishes both "Ambiguous Alpha" and "Ambiguous Beta", so it names neither.
    Last-write-wins files `D4`'s rule under "Ambiguous Beta" and produces a candidate for
    `d-ambiguous-beta` — a summary approved against a rule that may belong to Alpha. The
    pipeline's own guard deletes such an id (`assemble.py`, "issue #5") and this adopts it:
    the key is reported `unresolved` and nothing is drafted. Delete the two `del names_by_id`
    lines and this test fails with a candidate written.
    """
    report = write_report(
        tmp_path / "report.json",
        [finding("DRL-OUTSTANDING", AMBIGUOUS_KEY, key_field="summary_key")],
    )
    client = FakeClient()
    out = tmp_path / "out"

    outcome = run(
        repo, fixtures_dir, report, out, drafter=client, reviewer=client,
        classes=("detachment_rules",),
    )  # fmt: skip

    assert outcome.by_class["detachment_rules"].unresolved == (AMBIGUOUS_KEY,)
    assert outcome.by_class["detachment_rules"].kept == ()
    assert client.draft_calls == []
    assert not (out / "detachment-rules").exists()


# --------------------------------------------------------------------------------------
# Fix round 2 — B: a transport fault takes the partial-write path, end to end
# --------------------------------------------------------------------------------------


def test_a_transport_fault_through_the_real_client_keeps_the_paid_for_candidates(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    """Fix round 2, Important B — the receipt, through the real `SummaryClient`.

    No socket: the client is handed an `httpx.Client` on a `MockTransport`. The first entry
    completes; the second entry's draft call meets a `ConnectError`. Before the fix that escaped
    `SummaryClient` as itself, `draft_candidates` caught only `DraftingError`, and the first
    entry's paid-for candidate went with it. Remove the `except httpx.HTTPError` in
    `pipeline/summaries/client.py` and this test fails with a bare `ConnectError`.
    """
    import httpx

    from pipeline.summaries import SummaryClient

    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] > 2:
            raise httpx.ConnectError("an invented connection reset")
        body = json.loads(request.content)
        payload = (
            {"summary": "An invented candidate summary.", "used_verbatim": False}
            if "restate" in body["system"]
            else {"decision": "keep", "reason_code": "ok"}
        )
        return httpx.Response(
            200,
            json={
                "id": "msg_test",
                "type": "message",
                "role": "assistant",
                "model": DRAFT_MODEL,
                "content": [{"type": "text", "text": json.dumps(payload)}],
                "stop_reason": "end_turn",
            },
        )

    report = write_report(
        tmp_path / "report.json",
        [
            finding("SUM-MISSING", EMBER_KEY),
            finding("SUM-MISSING", VAULT_KEY),
        ],
    )
    out = tmp_path / "out"
    transport = httpx.Client(transport=httpx.MockTransport(handler))
    with SummaryClient(API_KEY, model=DRAFT_MODEL, http=transport) as client:
        outcome = run(repo, fixtures_dir, report, out, drafter=client, reviewer=client)

    assert outcome.failure is not None
    assert VAULT_KEY in outcome.failure
    # The first entry was billed before the reset; it is on disk.
    assert [r["ability_key"] for r in records(out, f"abilities/{UNASSIGNED}.json")] == [EMBER_KEY]
    # And the diagnostic names neither the entry text nor the transport's own message.
    for text in ALL_MECHANICS:
        assert text not in str(outcome.failure)
    assert "an invented connection reset" not in str(outcome.failure)


# --------------------------------------------------------------------------------------
# Fix round 2 — D: the drafted count is recorded, not inferred
# --------------------------------------------------------------------------------------


def test_an_entry_dropped_for_being_invalid_is_still_counted_as_drafted(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    """It was drafted and billed. The count says what this run spent, not what survived."""
    overlong = "INVENTED-OVERLENGTH " * 80
    report = write_report(
        tmp_path / "report.json",
        [finding("DRL-OUTSTANDING", DETACHMENT_KEY, key_field="summary_key")],
    )
    client = FakeClient(drafts={"Sacred Cadence": [Draft(overlong, False)]})

    outcome = run(
        repo, fixtures_dir, report, tmp_path / "out", drafter=client, reviewer=client,
        classes=("detachment_rules",),
    )  # fmt: skip

    assert outcome.by_class["detachment_rules"].dropped_invalid == (DETACHMENT_KEY,)
    assert outcome.by_class["detachment_rules"].kept == ()
    assert outcome.by_class["detachment_rules"].entries_drafted == 1


def test_a_rereview_key_the_reviewer_calls_lore_is_not_counted_as_drafted(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    """It never reached the drafting pass: one review call, no draft call."""
    authored(
        repo,
        f"abilities/{FACTION}.json",
        [approved_ability(EMBER_KEY, "Ember Shield", "An invented summary that carries flavour.")],
    )
    report = write_report(tmp_path / "report.json", [finding("SUM-NEEDS-REREVIEW", EMBER_KEY)])
    client = FakeClient(verdicts={"Ember Shield": [Verdict("lore", "lore-present")]})

    outcome = run(repo, fixtures_dir, report, tmp_path / "out", drafter=client, reviewer=client)

    assert client.draft_calls == []
    assert outcome.by_class["abilities"].dropped_lore == (EMBER_KEY,)
    assert outcome.by_class["abilities"].entries_drafted == 0


# --------------------------------------------------------------------------------------
# Fix round 2 — E: the resolution line, before the prompt
# --------------------------------------------------------------------------------------


def test_the_resolution_line_is_printed_before_the_confirmation_estimate(
    repo: Path, fixtures_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """One billed run: an unresolved count nobody sees until afterwards is unactionable."""
    report = write_report(
        tmp_path / "report.json",
        [
            finding("SUM-MISSING", VAULT_KEY),
            finding("SUM-MISSING", "datasheet:not-in-this-export"),
            finding("SUM-UNAPPROVED", CHITIN_KEY),
        ],
    )

    run(repo, fixtures_dir, report, tmp_path / "out", drafter=FakeClient(), reviewer=FakeClient())

    printed = capsys.readouterr().out
    line = "abilities: keys=2 resolved=1 unresolved=1 already-drafted=0 skipped-unapproved=1"
    assert line in printed
    assert printed.index(line) < printed.index("API calls"), "before the prompt, not after it"


def test_the_resolution_line_carries_no_mechanic_text(
    repo: Path, fixtures_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    report = write_report(
        tmp_path / "report.json",
        [
            finding("SUM-MISSING", VAULT_KEY),
            finding("DRL-OUTSTANDING", DETACHMENT_KEY, key_field="summary_key"),
        ],
    )
    with pytest.raises(ConfirmationRefused):
        run(
            repo, fixtures_dir, report, tmp_path / "out", drafter=ExplodingClient(),
            reviewer=ExplodingClient(), classes=("abilities", "detachment_rules"),
            assume_yes=False,
        )  # fmt: skip
    captured = capsys.readouterr()
    assert "keys=1 resolved=1" in captured.out
    for text in ALL_MECHANICS:
        assert text not in captured.out
        assert text not in captured.err


# --------------------------------------------------------------------------------------
# Record validity — Important 4
# --------------------------------------------------------------------------------------


def test_an_overlength_draft_is_dropped_by_key_and_the_rest_are_still_written(
    repo: Path, fixtures_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Fix round 1, Important 4 — the receipt.

    `DetachmentRuleSummary.summary` caps at 1 000 characters. An uncaught `ValidationError` both
    lost the class's candidates and rendered pydantic's truncated `input_value` repr — summary
    text — onto the terminal.
    """
    overlong = "INVENTED-OVERLENGTH " * 80
    assert len(overlong) > 1000
    report = write_report(
        tmp_path / "report.json",
        [
            finding("DRL-OUTSTANDING", DETACHMENT_KEY, key_field="summary_key"),
            finding("DRL-OUTSTANDING", ARTICLE_KEY, key_field="summary_key"),
        ],
    )
    client = FakeClient(drafts={"Sacred Cadence": [Draft(overlong, False)]})
    out = tmp_path / "out"

    outcome = run(
        repo, fixtures_dir, report, out, drafter=client, reviewer=client,
        classes=("detachment_rules",),
    )  # fmt: skip

    assert outcome.by_class["detachment_rules"].dropped_invalid == (DETACHMENT_KEY,)
    assert outcome.by_class["detachment_rules"].kept == (ARTICLE_KEY,)
    written = records(out, f"detachment-rules/{FACTION}.json")
    assert [record["summary_key"] for record in written] == [ARTICLE_KEY]
    captured = capsys.readouterr()
    assert "INVENTED-OVERLENGTH" not in captured.out
    assert "INVENTED-OVERLENGTH" not in captured.err
    assert DETACHMENT_KEY in captured.out


def test_every_candidate_validates_as_the_class_model(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    from pipeline.models.authored import AbilitySummary, DetachmentRuleSummary

    report = write_report(
        tmp_path / "report.json",
        [
            finding("SUM-MISSING", VAULT_KEY),
            finding("DRL-OUTSTANDING", DETACHMENT_KEY, key_field="summary_key"),
        ],
    )
    out = tmp_path / "out"
    run(
        repo, fixtures_dir, report, out, drafter=FakeClient(), reviewer=FakeClient(),
        classes=("abilities", "detachment_rules"),
    )  # fmt: skip
    for record in records(out, f"abilities/{UNASSIGNED}.json"):
        AbilitySummary.model_validate(record)
    for record in records(out, f"detachment-rules/{FACTION}.json"):
        DetachmentRuleSummary.model_validate(record)


# --------------------------------------------------------------------------------------
# Reporting, and the human/machine boundary — Minors 7 and 8
# --------------------------------------------------------------------------------------


def test_an_unapproved_key_is_reported_and_left_to_the_human_who_owns_it(
    repo: Path, fixtures_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Fix round 1, minor 8 — `-UNAPPROVED` means a curator has a draft in flight."""
    report = write_report(tmp_path / "report.json", [finding("SUM-UNAPPROVED", VAULT_KEY)])
    client = FakeClient()

    outcome = run(repo, fixtures_dir, report, tmp_path / "out", drafter=client, reviewer=client)

    assert outcome.by_class["abilities"].skipped_unapproved == (VAULT_KEY,)
    assert outcome.by_class["abilities"].kept == ()
    assert client.draft_calls == []
    assert "skipped-unapproved" in capsys.readouterr().out


def test_the_printed_count_says_entries_and_counts_entries(
    repo: Path, fixtures_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Fix round 1, minor 7 — a label that reads as a call count while counting entries."""
    report = write_report(tmp_path / "report.json", [finding("SUM-MISSING", VAULT_KEY)])
    client = FakeClient(
        verdicts={"Vault Cadence": [Verdict("redraft", "too-long"), Verdict("keep", "ok")]}
    )

    outcome = run(repo, fixtures_dir, report, tmp_path / "out", drafter=client, reviewer=client)

    assert len(client.draft_calls) == 2, "two calls"
    assert outcome.by_class["abilities"].entries_drafted == 1, "one entry"
    assert "entries-drafted=1" in capsys.readouterr().out


def test_a_key_the_source_does_not_publish_is_reported_not_guessed(
    repo: Path, fixtures_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    report = write_report(
        tmp_path / "report.json", [finding("SUM-MISSING", "datasheet:not-in-this-export")]
    )
    client = FakeClient()
    outcome = run(repo, fixtures_dir, report, tmp_path / "out", drafter=client, reviewer=client)
    assert outcome.by_class["abilities"].unresolved == ("datasheet:not-in-this-export",)
    assert client.draft_calls == []
    assert "datasheet:not-in-this-export" in capsys.readouterr().out


# --------------------------------------------------------------------------------------
# 010 R7c task 2 — the transport switch, and batched re-reviews
# --------------------------------------------------------------------------------------

#: Invented mechanic text for the many-key batching fixtures. Unmistakable on sight, like the
#: MECHANIC_* strings above: if one of these reaches stdout a test fails rather than a reviewer
#: having to notice.
BATCH_MECHANIC = "MECHANIC-THETA-{n:02d} invented models add {n} to an invented roll."


def batch_key(index: int) -> str:
    return f"datasheet:batch-ability-{index:02d}"


def batch_name(index: int) -> str:
    return f"Batch Ability {index:02d}"


def write_batch_abilities(fixtures_dir: Path, count: int) -> list[str]:
    """Rewrite the datasheet-ability table with ``count`` invented rows; return their keys."""
    rows = ["﻿datasheet_id|line|ability_id|model|name|description|type|parameter|"]
    for index in range(1, count + 1):
        rows.append(
            f"BV01|{index}|||{batch_name(index)}|{BATCH_MECHANIC.format(n=index)}|Datasheet||"
        )
    (fixtures_dir / "wahapedia" / "Datasheets_abilities.csv").write_text(
        "\n".join(rows) + "\n", encoding="utf-8", newline=""
    )
    return [batch_key(index) for index in range(1, count + 1)]


def approve_batch(repo: Path, count: int) -> None:
    """One approved curated record per batch key, so each is a re-review with a prior summary."""
    authored(
        repo,
        f"abilities/{FACTION}.json",
        [
            approved_ability(
                batch_key(index),
                batch_name(index),
                f"An invented summary a curator approved, number {index:02d}.",
            )
            for index in range(1, count + 1)
        ],
    )


@dataclass
class BatchClient(FakeClient):
    """The CLI shape: everything :class:`FakeClient` does, plus ``review_many``.

    Records the SIZE of every batch, because a batching path that quietly issued one call per
    item would still produce the right verdicts and the right totals.
    """

    batch_sizes: list[int] = field(default_factory=list)
    raise_on_batch: dict[int, DraftingError] = field(default_factory=dict)

    def review_many(self, items: Sequence[tuple[str, str, str]]) -> list[Verdict]:
        self.batch_sizes.append(len(items))
        failure = self.raise_on_batch.get(len(self.batch_sizes) - 1)
        if failure is not None:
            raise failure
        return [self.review(*item) for item in items]


def test_r7c_twenty_five_rereviews_are_issued_in_batches_of_ten_ten_five(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    """(c) The receipt for batching itself: the SIZES, not the total.

    Unbatched, these 25 keys are 25 `review` calls. Delete `_review_batch`'s batching arm and
    `batch_sizes` is empty, not `[10, 10, 5]`.
    """
    keys = write_batch_abilities(fixtures_dir, 25)
    approve_batch(repo, 25)
    report = write_report(
        tmp_path / "report.json", [finding("SUM-NEEDS-REREVIEW", key) for key in keys]
    )
    client = BatchClient()

    outcome = run(repo, fixtures_dir, report, tmp_path / "out", drafter=client, reviewer=client)

    assert client.batch_sizes == [10, 10, 5]
    assert client.draft_calls == [], "a kept re-review costs no draft"
    assert len(outcome.by_class["abilities"].rebaselined) == 25


def test_r7c_a_batch_routes_keep_lore_and_redraft_to_the_same_buckets_as_the_unbatched_path(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    """(d) One batch, three verdicts, three destinations — and the redraft is drafted."""
    keys = write_batch_abilities(fixtures_dir, 3)
    approve_batch(repo, 3)
    report = write_report(
        tmp_path / "report.json", [finding("SUM-NEEDS-REREVIEW", key) for key in keys]
    )
    client = BatchClient(
        verdicts={
            batch_name(1): [Verdict("keep", "ok")],
            batch_name(2): [Verdict("lore", "lore")],
            # The batch verdict, then the verdict on the fresh draft that follows it.
            batch_name(3): [Verdict("redraft", "incomplete"), Verdict("keep", "ok")],
        },
        drafts={batch_name(3): [Draft("An invented redrafted summary.", False)]},
    )
    out = tmp_path / "out"

    outcome = run(repo, fixtures_dir, report, out, drafter=client, reviewer=client)

    abilities = outcome.by_class["abilities"]
    assert client.batch_sizes == [3]
    assert abilities.rebaselined == (batch_key(1),)
    assert abilities.dropped_lore == (batch_key(2),)
    assert abilities.drafted == (batch_key(3),)
    assert sorted(abilities.kept) == sorted([batch_key(1), batch_key(3)])
    assert [call[0] for call in client.draft_calls] == [batch_name(3)]
    written = {
        record["ability_key"]: record for record in records(out, f"abilities/{FACTION}.json")
    }
    assert written[batch_key(3)]["summary"] == "An invented redrafted summary."
    # The redrafted re-baseline still carries the attribution pair (fix round 1's receipt).
    assert written[batch_key(3)]["digest_refreshed_at_version"] == VERSION


def test_r7c_a_failed_batch_keeps_the_candidates_already_produced(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    """(g) A `DraftingError` from `review_many` is the partial-write path, as a per-key one is."""
    keys = write_batch_abilities(fixtures_dir, 15)
    approve_batch(repo, 15)
    report = write_report(
        tmp_path / "report.json", [finding("SUM-NEEDS-REREVIEW", key) for key in keys]
    )
    out = tmp_path / "out"
    client = BatchClient(raise_on_batch={1: DraftingError(529)})

    outcome = run(repo, fixtures_dir, report, out, drafter=client, reviewer=client)

    abilities = outcome.by_class["abilities"]
    assert outcome.failure is not None
    assert batch_key(11) in outcome.failure, "the batch's first key names the stop"
    assert len(abilities.rebaselined) == 10
    assert sorted(abilities.not_attempted) == [batch_key(i) for i in range(11, 16)]
    on_disk = [record["ability_key"] for record in records(out, f"abilities/{FACTION}.json")]
    assert on_disk == [batch_key(i) for i in range(1, 11)], "the paid-for ten are on disk"


def test_r7c_a_reviewer_without_review_many_still_costs_one_call_per_key(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    """(h) The api shape. `_review_batch`'s fallback arm, and today's behaviour unchanged."""
    keys = write_batch_abilities(fixtures_dir, 12)
    approve_batch(repo, 12)
    report = write_report(
        tmp_path / "report.json", [finding("SUM-NEEDS-REREVIEW", key) for key in keys]
    )
    client = FakeClient()
    assert not hasattr(client, "review_many")

    outcome = run(repo, fixtures_dir, report, tmp_path / "out", drafter=client, reviewer=client)

    assert [call[0] for call in client.review_calls] == [batch_name(i) for i in range(1, 13)]
    assert len(outcome.by_class["abilities"].rebaselined) == 12


def test_r7c_the_batched_run_never_lets_the_mechanic_text_reach_stdout(
    repo: Path, fixtures_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """(i) The standing assertion, over the batched path this time."""
    keys = write_batch_abilities(fixtures_dir, 12)
    approve_batch(repo, 12)
    report = write_report(
        tmp_path / "report.json", [finding("SUM-NEEDS-REREVIEW", key) for key in keys]
    )
    client = BatchClient()

    run(repo, fixtures_dir, report, tmp_path / "out", drafter=client, reviewer=client)

    captured = capsys.readouterr()
    for index in range(1, 13):
        assert BATCH_MECHANIC.format(n=index) not in captured.out
        assert BATCH_MECHANIC.format(n=index) not in captured.err
    assert batch_key(1) in captured.out


def test_r7c_the_cli_cost_line_states_calls_and_no_token_figure(
    repo: Path, fixtures_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """(e) A token figure is a number that means nothing on a subscription seat."""
    keys = write_batch_abilities(fixtures_dir, 25)
    approve_batch(repo, 25)
    report = write_report(
        tmp_path / "report.json", [finding("SUM-NEEDS-REREVIEW", key) for key in keys]
    )
    client = BatchClient()

    run(
        repo,
        fixtures_dir,
        report,
        tmp_path / "out",
        drafter=client,
        reviewer=client,
        transport="cli",
    )

    printed = capsys.readouterr().out
    assert "3 CLI calls" in printed, "25 re-reviews batch into three calls"
    assert "tokens" not in printed
    assert "API calls" not in printed


def test_r7c_the_api_cost_line_is_unchanged(
    repo: Path, fixtures_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """(e) The billed transport still shows what it will be billed for."""
    report = write_report(
        tmp_path / "report.json",
        [finding("SUM-MISSING", VAULT_KEY), finding("SUM-MISSING", CHITIN_KEY)],
    )

    run(
        repo,
        fixtures_dir,
        report,
        tmp_path / "out",
        drafter=FakeClient(),
        reviewer=FakeClient(),
        transport="api",
    )

    printed = capsys.readouterr().out
    assert "4 API calls" in printed
    assert "tokens" in printed


def test_r7c_estimate_counts_a_batched_rereview_class_as_ceil_n_over_ten() -> None:
    """(f) The estimate is what the human says yes to; it must count the calls that happen."""
    from pipeline.models.authored import SummaryClass
    from tools.draft_summaries import MAX_BATCH_ITEMS, _estimate, _WorkList

    keys = tuple(batch_key(index) for index in range(1, 26))
    work = {SummaryClass.ABILITIES: _WorkList(rereview=keys)}
    texts = {SummaryClass.ABILITIES: {key: ("a name", "invented text") for key in keys}}
    drafted: dict[SummaryClass, set[str]] = {}

    batched, _tokens = _estimate(work, texts, drafted, batch_size=MAX_BATCH_ITEMS)
    serial, _serial_tokens = _estimate(work, texts, drafted, batch_size=None)

    assert batched == 3
    assert serial == 25


# --------------------------------------------------------------------------------------
# 010 R7c task 2 — `--transport`, and the API key the cli path must not need
# --------------------------------------------------------------------------------------

ENV_NO_KEY = {name: value for name, value in ENV.items() if name != "WGC_ANTHROPIC_API_KEY"}


class _RecordingCli(BatchClient):
    """Stands in for `CliSummaryClient` in `main`, recording how it was constructed."""

    built: list[dict[str, Any]] = []

    def __init__(self, *, model: str, executable: str = "claude") -> None:
        super().__init__()
        type(self).built.append({"model": model, "executable": executable})


def _never_built(**kwargs: Any) -> Any:
    raise AssertionError("the cli client was built on the api transport")


def test_r7c_the_default_transport_builds_the_cli_client_and_needs_no_api_key(
    repo: Path, fixtures_dir: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """(a) The whole point: a subscription run that never reads `anthropic_api_key`."""
    monkeypatch.setattr("pipeline.summaries.CliSummaryClient", _RecordingCli)
    _RecordingCli.built = []
    report = write_report(tmp_path / "report.json", [finding("SUM-MISSING", VAULT_KEY)])

    code = main(
        _refusal_argv(repo, fixtures_dir, report, tmp_path / "out"), env=ENV_NO_KEY, clients=None
    )

    assert code == 0
    assert [entry["model"] for entry in _RecordingCli.built] == [DRAFT_MODEL, REVIEW_MODEL]
    assert {entry["executable"] for entry in _RecordingCli.built} == {"claude"}
    assert records(tmp_path / "out", f"abilities/{UNASSIGNED}.json")


def test_r7c_an_explicit_api_transport_still_refuses_an_empty_api_key(
    repo: Path, fixtures_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """(b) The guard belongs to the api path, and still fires there."""
    report = write_report(tmp_path / "report.json", [finding("SUM-MISSING", VAULT_KEY)])
    client = FakeClient()

    code = main(
        [*_refusal_argv(repo, fixtures_dir, report, tmp_path / "out"), "--transport", "api"],
        env=ENV_NO_KEY,
        clients=(client, client),
    )

    assert code == 60
    assert "WGC_ANTHROPIC_API_KEY" in capsys.readouterr().err
    assert client.draft_calls == []


def test_r7c_an_explicit_api_transport_builds_the_api_client(
    repo: Path, fixtures_dir: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """(b) `--transport api` overrides the config's `cli` default."""
    built: list[str] = []

    class _RecordingApi(FakeClient):
        def __init__(self, api_key: str, *, model: str) -> None:
            super().__init__()
            built.append(model)

        def __enter__(self) -> _RecordingApi:
            return self

        def __exit__(self, *args: Any) -> None:
            return None

    monkeypatch.setattr("pipeline.summaries.SummaryClient", _RecordingApi)
    monkeypatch.setattr("pipeline.summaries.CliSummaryClient", _never_built)
    report = write_report(tmp_path / "report.json", [finding("SUM-MISSING", VAULT_KEY)])

    code = main(
        [*_refusal_argv(repo, fixtures_dir, report, tmp_path / "out"), "--transport", "api"],
        env=ENV,
        clients=None,
    )

    assert code == 0
    assert built == [DRAFT_MODEL, REVIEW_MODEL]


# --------------------------------------------------------------------------------------
# 010 R7c task 2, fix round 1 — the two partial-write paths the restructure created
# --------------------------------------------------------------------------------------


@dataclass
class ShortBatchClient(BatchClient):
    """A batching reviewer that returns the WRONG NUMBER of verdicts for chosen batches.

    Unreachable through the real `CliSummaryClient`, which length-checks its own reply and
    raises `cli-batch-shape` first. This client stands in for the shape that check exists to
    catch, so the tool's own handling of it is exercised rather than assumed.
    """

    short_batches: set[int] = field(default_factory=set)

    def review_many(self, items: Sequence[tuple[str, str, str]]) -> list[Verdict]:
        verdicts = super().review_many(items)
        if len(self.batch_sizes) - 1 in self.short_batches:
            return verdicts[:-1]
        return verdicts


def test_r7c_fix1_a_phase_two_failure_keeps_the_candidates_phase_one_produced(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    """Fix round 1, Important 1 — the partial-write path the restructure newly created.

    A re-baseline is a candidate produced in the re-review phase, *before* a single draft call is
    made. If those candidates were written only after the drafting phase, a `DraftingError` on
    any redrafted key would discard every re-baseline the same class already paid for. Move the
    phase-1 `_add` to after the drafting loop and this test fails with an empty candidates file.
    """
    keys = write_batch_abilities(fixtures_dir, 3)
    approve_batch(repo, 3)
    report = write_report(
        tmp_path / "report.json", [finding("SUM-NEEDS-REREVIEW", key) for key in keys]
    )
    out = tmp_path / "out"
    client = BatchClient(
        verdicts={
            batch_name(1): [Verdict("keep", "ok")],
            batch_name(2): [Verdict("redraft", "incomplete")],
            batch_name(3): [Verdict("redraft", "incomplete")],
        },
        raise_on_draft={batch_name(2): DraftingError(529)},
    )

    outcome = run(repo, fixtures_dir, report, out, drafter=client, reviewer=client)

    abilities = outcome.by_class["abilities"]
    assert outcome.failure is not None
    assert batch_key(2) in outcome.failure
    assert abilities.rebaselined == (batch_key(1),)
    assert abilities.not_attempted == (batch_key(3),)
    # The one the re-review phase paid for is on disk, though the drafting phase then failed.
    on_disk = [record["ability_key"] for record in records(out, f"abilities/{FACTION}.json")]
    assert on_disk == [batch_key(1)]


def test_r7c_fix1_a_batch_of_the_wrong_length_keeps_what_was_paid_for(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    """Fix round 1, Important 2 — a mismatched reply is a stop, not a traceback.

    `zip(..., strict=True)` raised `ValueError`, which no handler in `_run_class`,
    `draft_candidates` or `main` catches: the whole class's already-paid-for candidates went with
    it. Restore the bare `zip(...)`/`strict=True` and drop the length check and this test fails
    with `ValueError` instead of reporting a failure.
    """
    keys = write_batch_abilities(fixtures_dir, 15)
    approve_batch(repo, 15)
    report = write_report(
        tmp_path / "report.json", [finding("SUM-NEEDS-REREVIEW", key) for key in keys]
    )
    out = tmp_path / "out"
    client = ShortBatchClient(short_batches={1})

    outcome = run(repo, fixtures_dir, report, out, drafter=client, reviewer=client)

    abilities = outcome.by_class["abilities"]
    assert outcome.failure is not None
    assert batch_key(11) in outcome.failure
    assert "cli-batch-shape" in outcome.failure
    assert len(abilities.rebaselined) == 10
    assert sorted(abilities.not_attempted) == [batch_key(i) for i in range(11, 16)]
    on_disk = [record["ability_key"] for record in records(out, f"abilities/{FACTION}.json")]
    assert on_disk == [batch_key(i) for i in range(1, 11)], "the paid-for ten are on disk"


# --------------------------------------------------------------------------------------
# 010 R8 task 3: data_dir is derived from the build the report came from, never the
# committed data/ tree. Round 7d found the cause first-hand: a stale default resolved
# detachment ids against `repository_root/data` regardless of which build the report was
# for, so all seven detachment-rule keys new since round 6 were silently dropped.
# --------------------------------------------------------------------------------------

#: A detachment id invented for this section only, absent from the `repo` fixture's committed
#: `data/` tree -- that absence IS the bug this section exists to catch. Were the default still
#: falling back to `repository_root/data`, every key below would be unresolved.
ROUND8_FACTION = "f-round8"
ROUND8_DETACHMENT_ID = "d-round8-only-detachment"
ROUND8_RULE_COUNT = 7

ROUND8_DETACHMENTS_CSV = "﻿id|faction_id|name|legend|type|\nD9|F9|Round Eight Detachment|||\n"
ROUND8_DETACHMENT_ABILITIES_CSV = "﻿id|detachment_id|name|legend|description|\n" + "".join(
    f"DA9{i}|D9|Round Eight Rule {i}||MECHANIC-R8-{i} an invented rule text for rule {i}.|\n"
    for i in range(1, ROUND8_RULE_COUNT + 1)
)


def round8_keys() -> list[str]:
    """The 7 outstanding detachment-rule keys this section's report carries."""
    return [
        f"detachment:{ROUND8_DETACHMENT_ID}:round-eight-rule-{i}"
        for i in range(1, ROUND8_RULE_COUNT + 1)
    ]


@pytest.fixture
def round8_fixtures_dir(tmp_path: Path) -> Path:
    """A fresh copy of the minimal fixture set, carrying only the round-8 detachment rows."""
    root = tmp_path / "round8-fixtures"
    shutil.copytree(MINIMAL, root)
    wahapedia = root / "wahapedia"
    (wahapedia / "Detachments.csv").write_text(ROUND8_DETACHMENTS_CSV, encoding="utf-8", newline="")
    (wahapedia / "Detachment_abilities.csv").write_text(
        ROUND8_DETACHMENT_ABILITIES_CSV, encoding="utf-8", newline=""
    )
    return root


def write_round8_build_tree(run_root: Path) -> Path:
    """``<run_root>/out/data/<edition>/factions/<faction>/detachments.json``.

    The layout ``live_build.py`` produces, carrying the id ``repo``'s committed ``data/`` tree
    does not.
    """
    data_dir = run_root / "out" / "data"
    faction_dir = data_dir / "wh40k-11e" / "factions" / ROUND8_FACTION
    faction_dir.mkdir(parents=True)
    (faction_dir / "detachments.json").write_text(
        json.dumps(
            {
                "detachments": [
                    {
                        "detachment_id": ROUND8_DETACHMENT_ID,
                        "name": "Round Eight Detachment",
                        "rules": [],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    return data_dir


def write_round8_report(run_root: Path, rules_version_id: str = "round8-id") -> Path:
    """``<run_root>/reports/<rules_version_id>/report.json`` -- the layout ``report_dir`` writes."""
    path = run_root / "reports" / rules_version_id / "report.json"
    path.parent.mkdir(parents=True)
    findings = [finding("DRL-OUTSTANDING", key, key_field="summary_key") for key in round8_keys()]
    return write_report(path, findings)


def test_no_data_flag_and_no_out_data_dir_refuses_with_a_configerror_naming_data(
    repo: Path, round8_fixtures_dir: Path, tmp_path: Path
) -> None:
    """Requirement (a), the refusal half.

    ``repo``'s committed ``data/`` tree exists and is perfectly readable -- that is exactly the
    trap: the old default silently read it regardless of which build the report came from. The
    report here sits loose under ``tmp_path``, with no ``<run root>/out/data`` anywhere above
    it, so the tool must refuse rather than fall back.
    """
    report = write_report(tmp_path / "report.json", [finding("SUM-MISSING", VAULT_KEY)])

    with pytest.raises(ConfigError, match="--data"):
        draft_candidates(
            load_config(env=ENV),
            transport="api",
            repository_root=repo,
            report_path=report,
            out_dir=tmp_path / "candidates",
            version=VERSION,
            classes=("abilities",),
            drafter=FakeClient(),
            reviewer=FakeClient(),
            fixtures_dir=round8_fixtures_dir,
            offline=True,
            assume_yes=True,
        )


def test_data_dir_is_derived_from_the_reports_run_root_and_named_in_the_resolution_table(
    repo: Path, round8_fixtures_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Requirements (a) (the derivation half) and (c).

    No ``--data`` is given. The report sits at ``<run_root>/reports/<id>/report.json``, exactly
    where a real build's ``report_dir`` writes it, and ``<run_root>/out/data`` carries the id
    ``repo``'s committed tree does not. The resolution table must print the ``data_dir`` this
    run actually used, so a human reading it before the confirmation prompt can tell whether it
    is the one the report came from.
    """
    run_root = tmp_path / "run"
    data_dir = write_round8_build_tree(run_root)
    report = write_round8_report(run_root)

    draft_candidates(
        load_config(env=ENV),
        transport="api",
        repository_root=repo,
        report_path=report,
        out_dir=tmp_path / "candidates",
        version=VERSION,
        classes=("detachment_rules",),
        drafter=FakeClient(),
        reviewer=FakeClient(),
        fixtures_dir=round8_fixtures_dir,
        offline=True,
        assume_yes=True,
    )

    captured = capsys.readouterr()
    assert str(data_dir) in captured.out


def test_seven_keys_from_a_detachment_id_absent_from_committed_data_all_resolve(
    repo: Path, round8_fixtures_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Requirement (b) -- the round-6-through-8 regression, closed.

    All 7 keys name a detachment id ``repo``'s committed ``data/`` tree has never carried. Were
    ``data_dir`` still defaulting to ``repository_root/data``, ``curated_detachments`` would
    resolve nothing for this id, ``detachment_rule_texts`` would ``continue`` past every key,
    and the resolution line would read ``resolved=0 unresolved=7`` -- the exact silent-skip this
    task exists to close.
    """
    run_root = tmp_path / "run"
    write_round8_build_tree(run_root)
    report = write_round8_report(run_root)

    outcome = draft_candidates(
        load_config(env=ENV),
        transport="api",
        repository_root=repo,
        report_path=report,
        out_dir=tmp_path / "candidates",
        version=VERSION,
        classes=("detachment_rules",),
        drafter=FakeClient(),
        reviewer=FakeClient(),
        fixtures_dir=round8_fixtures_dir,
        offline=True,
        assume_yes=True,
    )

    captured = capsys.readouterr()
    assert "detachment_rules: keys=7 resolved=7 unresolved=0" in captured.out
    assert sorted(outcome.by_class["detachment_rules"].kept) == sorted(round8_keys())


def test_default_data_dir_does_not_escape_the_report_run_root_to_an_unrelated_ancestors_build(
    tmp_path: Path,
) -> None:
    """Fix round 1 (code review). ``_default_data_dir`` must be bounded to the report's own run
    root, not walk to the first ``out/data`` found at any ancestor.

    ``scratch/`` here stands in for shared scratch space carrying leftovers from a *different*
    run: ``scratch/out/data`` belongs to that other run, not to this one. This run's own root,
    ``scratch/run-a``, has no ``out/data`` of its own -- its report sits at
    ``scratch/run-a/reports/<id>/report.json``, exactly where ``report_dir`` writes it. An
    unbounded walk up the parents would pass ``scratch/run-a`` (no ``out/data``) and keep going
    to find ``scratch/out/data`` -- the unrelated other run's build -- and return that. The
    correct behaviour is to stop at ``scratch/run-a`` and report ``None``, exactly as if no
    ``out/data`` existed anywhere.
    """
    scratch = tmp_path / "scratch"
    other_run_data_dir = scratch / "out" / "data"
    other_run_data_dir.mkdir(parents=True)
    (other_run_data_dir / "marker.json").write_text("{}", encoding="utf-8")

    run_root = scratch / "run-a"
    report_path = run_root / "reports" / "round8-id" / "report.json"
    report_path.parent.mkdir(parents=True)
    report_path.write_text("{}", encoding="utf-8")

    result = _default_data_dir(report_path)

    assert result is None, (
        f"expected None (run root has no out/data of its own), got {result!r} -- "
        "the unbounded walk escaped to an unrelated ancestor's out/data"
    )


# --------------------------------------------------------------------------------------
# 010 R8 task 3: --rebaseline-authorization -- task 5 invokes this tool with a round-8
# citation the module's own hard-coded ruling-6 string cannot name.
# --------------------------------------------------------------------------------------


def test_rebaseline_authorization_defaults_to_the_module_constant(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    authored(
        repo,
        f"abilities/{FACTION}.json",
        [approved_ability(EMBER_KEY, "Ember Shield", "An invented summary a curator approved.")],
    )
    report = write_report(tmp_path / "report.json", [finding("SUM-NEEDS-REREVIEW", EMBER_KEY)])
    out = tmp_path / "candidates"

    run(repo, fixtures_dir, report, out, drafter=FakeClient(), reviewer=FakeClient())

    record = records(out, f"abilities/{FACTION}.json")[0]
    assert record["digest_refreshed_under_authorization"] == REBASELINE_AUTHORIZATION


def test_rebaseline_authorization_cli_flag_overrides_the_default(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    """The exact interface task 5 needs: ``--rebaseline-authorization <citation>``."""
    authored(
        repo,
        f"abilities/{FACTION}.json",
        [approved_ability(EMBER_KEY, "Ember Shield", "An invented summary a curator approved.")],
    )
    report = write_report(tmp_path / "report.json", [finding("SUM-NEEDS-REREVIEW", EMBER_KEY)])
    out = tmp_path / "candidates"
    citation = "owner-2026-09-15-text-integrity-rereview"
    client = FakeClient()

    code = main(
        [
            *_refusal_argv(repo, fixtures_dir, report, out),
            "--classes",
            "abilities",
            "--rebaseline-authorization",
            citation,
        ],
        env=ENV,
        clients=(client, client),
    )

    assert code == int(ExitCode.SUCCESS)
    record = records(out, f"abilities/{FACTION}.json")[0]
    assert record["digest_refreshed_under_authorization"] == citation
    assert record["digest_refreshed_under_authorization"] != REBASELINE_AUTHORIZATION
