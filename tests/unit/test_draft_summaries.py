# AI-Assisted: Claude Code (model: claude-opus-5) - Asserts the summary drafting tool (010 R7
# task 2): it drives the Task-1 client over a build report's outstanding summary findings and
# writes CANDIDATE records to a scratch directory, never to curation/, and never lets the
# export's mechanic text reach stdout (amended standing rule 3, 2026-09-14).
# AI-Assisted: Claude Code (model: claude-opus-5) - 010 R7 task 2 fix round 1: receipts for the
# attribution pair on a redrafted re-review candidate, the build-resolved detachment id (with the
# leading-article divergence that the old slug derivation got wrong), resume/per-class writes/
# DraftingError survival, the per-record validation drop, the per-faction layout, the second
# curation-root refusal, the entries-vs-calls label, and the -UNAPPROVED skip.
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

from pipeline.summaries import Draft, DraftingError, Verdict
from tools.draft_summaries import (
    REBASELINE_AUTHORIZATION,
    UNASSIGNED,
    ConfirmationRefused,
    DraftRun,
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

FACTION = "f-invented"

ABILITIES_CSV = f"﻿id|name|legend|faction_id|description|\nA1|Chitin Bloom||F1|{MECHANIC_CHITIN}|\n"
DATASHEETS_ABILITIES_CSV = (
    "﻿datasheet_id|line|ability_id|model|name|description|type|parameter|\n"
    f"AV01|1|||Vault Cadence|{MECHANIC_VAULT}|Datasheet||\n"
    "AV01|2|A1||||Faction||\n"
    f"AV01|3|||Ember Shield|{MECHANIC_EMBER}|Datasheet||\n"
)
DETACHMENTS_CSV = (
    "﻿id|faction_id|name|legend|type|\nD1|F1|Invented Vanguard|||\nD2|F1|Ironstorm Spearhead|||\n"
)
DETACHMENT_ABILITIES_CSV = (
    "﻿id|detachment_id|name|legend|description|\n"
    f"DA1|D1|Sacred Cadence||{MECHANIC_CADENCE}|\n"
    f"DA2|D2|Storm Cadence||{MECHANIC_STORM}|\n"
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
) -> DraftRun:
    from pipeline.config import load_config

    return draft_candidates(
        load_config(env=ENV),
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


ALL_MECHANICS = (MECHANIC_VAULT, MECHANIC_CHITIN, MECHANIC_EMBER, MECHANIC_CADENCE, MECHANIC_STORM)


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
