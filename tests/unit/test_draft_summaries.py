# AI-Assisted: Claude Code (model: claude-opus-5) - Asserts the summary drafting tool (010 R7
# task 2): it drives the Task-1 client over a build report's outstanding summary findings and
# writes CANDIDATE records to a scratch directory, never to curation/, and never lets the
# export's mechanic text reach stdout (amended standing rule 3, 2026-09-14).
"""What this tool has to be trusted about is what it refuses to do.

The candidates it produces are read by the Owner and merged by hand, so the record shape is
asserted. But the four tests that earn it the right to run against the live source are
:func:`test_it_refuses_an_out_directory_inside_the_repository_curation_tree`,
:func:`test_the_mechanic_text_never_reaches_stdout`,
:func:`test_without_yes_and_non_interactive_it_refuses_before_any_api_call`, and
:func:`test_nothing_is_written_under_curation`.

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

from pipeline.summaries import Draft, Verdict
from tools.draft_summaries import (
    REBASELINE_AUTHORIZATION,
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

ENV = {
    "WGC_DETAIL_EDITION": "wh40k-11e",
    "WGC_MECHANIC_DIGEST_KEY": KEY,
    "WGC_DRAFT_MODEL": DRAFT_MODEL,
    "WGC_REVIEW_MODEL": REVIEW_MODEL,
}

# The invented mechanic text of the fixture export. Never a paraphrase of anything real.
MECHANIC_VAULT = "MECHANIC-ALPHA each time this unit invents a move, add 2 to the invented roll."
MECHANIC_CHITIN = "MECHANIC-BETA models in this unit add 1 to every invented saving throw."
MECHANIC_EMBER = "MECHANIC-GAMMA on an invented roll of 6, ignore the invented wound."
MECHANIC_CADENCE = "MECHANIC-DELTA each unit may invent one extra action in each phase."

VAULT_KEY = "datasheet:vault-cadence"
CHITIN_KEY = "faction:chitin-bloom"
EMBER_KEY = "datasheet:ember-shield"
DETACHMENT_KEY = "detachment:d-invented-vanguard:sacred-cadence"

ABILITIES_CSV = f"﻿id|name|legend|faction_id|description|\nA1|Chitin Bloom||F1|{MECHANIC_CHITIN}|\n"
DATASHEETS_ABILITIES_CSV = (
    "﻿datasheet_id|line|ability_id|model|name|description|type|parameter|\n"
    f"AV01|1|||Vault Cadence|{MECHANIC_VAULT}|Datasheet||\n"
    "AV01|2|A1||||Faction||\n"
    f"AV01|3|||Ember Shield|{MECHANIC_EMBER}|Datasheet||\n"
)
DETACHMENTS_CSV = "﻿id|faction_id|name|legend|type|\nD1|F1|Invented Vanguard|||\n"
DETACHMENT_ABILITIES_CSV = (
    f"﻿id|detachment_id|name|legend|description|\nDA1|D1|Sacred Cadence||{MECHANIC_CADENCE}|\n"
)


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
    draft_calls: list[tuple[str, str, str]] = field(default_factory=list)
    review_calls: list[tuple[str, str, str]] = field(default_factory=list)

    def draft(
        self,
        name: str,
        mechanic_text: str,
        *,
        ability_class: Literal["ability", "detachment_rule"],
    ) -> Draft:
        self.draft_calls.append((name, mechanic_text, ability_class))
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
        raise AssertionError("draft() was called before the confirmation gate passed")

    def review(self, *args: Any, **kwargs: Any) -> Verdict:
        raise AssertionError("review() was called before the confirmation gate passed")


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
    """A stand-in repository root: a `work/` the run may use and a `curation/` it may not."""
    (tmp_path / "repo" / "work").mkdir(parents=True)
    (tmp_path / "repo" / "curation" / "abilities").mkdir(parents=True)
    (tmp_path / "repo" / "curation" / "detachment-rules").mkdir(parents=True)
    return tmp_path / "repo"


def write_report(path: Path, findings: Sequence[dict[str, Any]]) -> Path:
    path.write_text(json.dumps({"findings": list(findings)}), encoding="utf-8")
    return path


def finding(code: str, key: str, *, key_field: str = "ability_key") -> dict[str, Any]:
    return {"finding_code": code, "entity_refs": [key], "detail": {key_field: key}}


def authored(repo: Path, relative: str, records: Sequence[dict[str, Any]]) -> None:
    path = repo / "curation" / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(list(records), indent=2), encoding="utf-8")


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


# --------------------------------------------------------------------------------------
# (a) a missing ability key becomes one candidate, digested from the current source
# --------------------------------------------------------------------------------------


def test_a_missing_ability_key_yields_one_candidate_with_the_current_digest(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    from pipeline.acquire.detail_source import acquire_detail, read_detail
    from pipeline.config import load_config
    from pipeline.curate.summaries import compute_current_digests

    report = write_report(tmp_path / "report.json", [finding("SUM-MISSING", VAULT_KEY)])
    client = FakeClient(drafts={"Vault Cadence": [Draft("An invented mechanic summary.", False)]})
    out = tmp_path / "candidates"

    outcome = run(repo, fixtures_dir, report, out, drafter=client, reviewer=client)

    config = load_config(env=ENV)
    _acq, payloads = acquire_detail(config, fixtures_dir=fixtures_dir, offline=True)
    expected = compute_current_digests(read_detail(payloads), key=KEY.encode("utf-8"))

    written = records(out, "abilities/candidates.json")
    assert [record["ability_key"] for record in written] == [VAULT_KEY]
    assert written[0]["mechanic_digest"] == expected[VAULT_KEY]
    assert written[0]["review_state"] == "approved"
    assert written[0]["reviewed_by"] == f"{REVIEW_MODEL}-reviewer"
    assert written[0]["summary"] == "An invented mechanic summary."
    assert written[0]["authored_against_acquisition"]
    assert "digest_refreshed_at_version" not in written[0]
    assert outcome.by_class["abilities"].kept == (VAULT_KEY,)


def test_the_client_is_asked_for_a_draft_then_a_review(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    report = write_report(tmp_path / "report.json", [finding("SUM-MISSING", VAULT_KEY)])
    client = FakeClient()

    run(repo, fixtures_dir, report, tmp_path / "out", drafter=client, reviewer=client)

    assert [call[0] for call in client.draft_calls] == ["Vault Cadence"]
    assert client.draft_calls[0][2] == "ability"
    assert [call[0] for call in client.review_calls] == ["Vault Cadence"]


# --------------------------------------------------------------------------------------
# (b) a re-review key the reviewer keeps becomes a re-baseline candidate
# --------------------------------------------------------------------------------------


def test_a_kept_rereview_key_yields_a_rebaseline_candidate_with_both_attribution_fields(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    from pipeline.acquire.detail_source import acquire_detail, read_detail
    from pipeline.config import load_config
    from pipeline.curate.summaries import compute_current_digests

    authored(
        repo,
        "abilities/f-invented.json",
        [
            {
                "ability_key": EMBER_KEY,
                "name": "Ember Shield",
                "summary": "An invented summary a curator already approved.",
                "review_state": "approved",
                "mechanic_digest": "0" * 32,
                "reviewed_by": "someone-else",
                "reviewed_at": "2026-01-01T00:00:00Z",
            }
        ],
    )
    report = write_report(tmp_path / "report.json", [finding("SUM-NEEDS-REREVIEW", EMBER_KEY)])
    client = FakeClient()
    out = tmp_path / "candidates"

    outcome = run(repo, fixtures_dir, report, out, drafter=client, reviewer=client)

    config = load_config(env=ENV)
    _acq, payloads = acquire_detail(config, fixtures_dir=fixtures_dir, offline=True)
    expected = compute_current_digests(read_detail(payloads), key=KEY.encode("utf-8"))

    written = records(out, "abilities/candidates.json")
    assert [record["ability_key"] for record in written] == [EMBER_KEY]
    record = written[0]
    # The NEW digest, not the stale one the curated record was approved against.
    assert record["mechanic_digest"] == expected[EMBER_KEY]
    assert record["mechanic_digest"] != "0" * 32
    assert record["digest_refreshed_at_version"] == VERSION
    assert record["digest_refreshed_under_authorization"] == REBASELINE_AUTHORIZATION
    # The approved summary is carried across unchanged; the reviewer said keep, not redraft.
    assert record["summary"] == "An invented summary a curator already approved."
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
# (c) a re-review key the reviewer rejects is drafted fresh
# --------------------------------------------------------------------------------------


def test_a_rereview_key_the_reviewer_rejects_is_drafted_fresh(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    authored(
        repo,
        "abilities/f-invented.json",
        [
            {
                "ability_key": EMBER_KEY,
                "name": "Ember Shield",
                "summary": "An invented summary that no longer describes the mechanic.",
                "review_state": "approved",
                "mechanic_digest": "0" * 32,
            }
        ],
    )
    report = write_report(tmp_path / "report.json", [finding("SUM-NEEDS-REREVIEW", EMBER_KEY)])
    client = FakeClient(
        verdicts={"Ember Shield": [Verdict("redraft", "meaning-changed"), Verdict("keep", "ok")]},
        drafts={"Ember Shield": [Draft("A freshly invented summary.", False)]},
    )
    out = tmp_path / "candidates"

    outcome = run(repo, fixtures_dir, report, out, drafter=client, reviewer=client)

    written = records(out, "abilities/candidates.json")
    assert written[0]["summary"] == "A freshly invented summary."
    assert [call[0] for call in client.draft_calls] == ["Ember Shield"]
    # Redrafted, so it is a fresh authorship rather than a carried approval: no attribution pair.
    assert "digest_refreshed_under_authorization" not in written[0]
    assert outcome.by_class["abilities"].kept == (EMBER_KEY,)
    assert outcome.by_class["abilities"].rebaselined == ()


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
    assert records(out, "abilities/candidates.json")[0]["summary"] == "Second try."
    assert outcome.by_class["abilities"].redrafted == (VAULT_KEY,)


# --------------------------------------------------------------------------------------
# (d) two lore verdicts drop the key and list it
# --------------------------------------------------------------------------------------


def test_two_lore_verdicts_drop_the_key_and_list_it(
    repo: Path, fixtures_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    report = write_report(tmp_path / "report.json", [finding("SUM-MISSING", VAULT_KEY)])
    client = FakeClient(
        verdicts={
            "Vault Cadence": [
                Verdict("lore", "lore-present"),
                Verdict("lore", "lore-present"),
            ]
        }
    )
    out = tmp_path / "candidates"

    outcome = run(repo, fixtures_dir, report, out, drafter=client, reviewer=client)

    assert outcome.by_class["abilities"].dropped_lore == (VAULT_KEY,)
    assert outcome.by_class["abilities"].kept == ()
    assert not (out / "abilities" / "candidates.json").exists()
    printed = capsys.readouterr().out
    assert VAULT_KEY in printed
    assert "dropped" in printed


# --------------------------------------------------------------------------------------
# (e) the tool refuses an --out inside curation/
# --------------------------------------------------------------------------------------


def test_it_refuses_an_out_directory_inside_the_repository_curation_tree(
    repo: Path, fixtures_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    report = write_report(tmp_path / "report.json", [finding("SUM-MISSING", VAULT_KEY)])
    code = main(
        [
            "--report",
            str(report),
            "--out",
            str(repo / "curation" / "abilities" / "candidates"),
            "--version",
            VERSION,
            "--repo",
            str(repo),
            "--fixtures",
            str(fixtures_dir),
            "--offline",
            "--yes",
        ],
        env=ENV,
    )
    assert code == 60
    assert "curation" in capsys.readouterr().err


def test_it_refuses_an_out_directory_that_reaches_curation_through_a_relative_path(
    repo: Path, fixtures_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    report = write_report(tmp_path / "report.json", [finding("SUM-MISSING", VAULT_KEY)])
    code = main(
        [
            "--report",
            str(report),
            "--out",
            str(repo / "work" / ".." / "curation" / "sneaky"),
            "--version",
            VERSION,
            "--repo",
            str(repo),
            "--fixtures",
            str(fixtures_dir),
            "--offline",
            "--yes",
        ],
        env=ENV,
    )
    # Also assert WHY: an unset API key would otherwise exit 60 too, and this test would pass
    # with the refusal deleted.
    assert code == 60
    assert "curation" in capsys.readouterr().err


def test_it_refuses_curation_itself(
    repo: Path, fixtures_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    report = write_report(tmp_path / "report.json", [finding("SUM-MISSING", VAULT_KEY)])
    code = main(
        [
            "--report",
            str(report),
            "--out",
            str(repo / "curation"),
            "--version",
            VERSION,
            "--repo",
            str(repo),
            "--fixtures",
            str(fixtures_dir),
            "--offline",
            "--yes",
        ],
        env=ENV,
    )
    assert code == 60
    assert "curation" in capsys.readouterr().err


def test_nothing_is_written_under_curation(repo: Path, fixtures_dir: Path, tmp_path: Path) -> None:
    before = sorted(p.relative_to(repo) for p in (repo / "curation").rglob("*"))
    report = write_report(tmp_path / "report.json", [finding("SUM-MISSING", VAULT_KEY)])
    run(repo, fixtures_dir, report, tmp_path / "out", drafter=FakeClient(), reviewer=FakeClient())
    after = sorted(p.relative_to(repo) for p in (repo / "curation").rglob("*"))
    assert before == after


# --------------------------------------------------------------------------------------
# (f) the export's mechanic text never reaches stdout
# --------------------------------------------------------------------------------------


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
    for text in (MECHANIC_VAULT, MECHANIC_CHITIN, MECHANIC_EMBER, MECHANIC_CADENCE):
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
# Ruling 2: --limit, and the confirmation gate
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

    assert len(records(out, "abilities/candidates.json")) == 2
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
    out = tmp_path / "out"

    outcome = run(
        repo,
        fixtures_dir,
        report,
        out,
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
# The detachment-rule class
# --------------------------------------------------------------------------------------


def test_a_detachment_rule_finding_yields_a_candidate_in_its_own_class_file(
    repo: Path, fixtures_dir: Path, tmp_path: Path
) -> None:
    report = write_report(
        tmp_path / "report.json",
        [finding("DRL-OUTSTANDING", DETACHMENT_KEY, key_field="summary_key")],
    )
    client = FakeClient()
    out = tmp_path / "out"

    run(
        repo,
        fixtures_dir,
        report,
        out,
        drafter=client,
        reviewer=client,
        classes=("detachment_rules",),
    )

    written = records(out, "detachment-rules/candidates.json")
    assert [record["summary_key"] for record in written] == [DETACHMENT_KEY]
    assert written[0]["detachment_id"] == "d-invented-vanguard"
    assert written[0]["name"] == "Sacred Cadence"
    assert client.draft_calls[0][2] == "detachment_rule"
    assert not (out / "abilities" / "candidates.json").exists()


# --------------------------------------------------------------------------------------
# Shape: the candidates validate as the class's own authored model
# --------------------------------------------------------------------------------------


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
        repo,
        fixtures_dir,
        report,
        out,
        drafter=FakeClient(),
        reviewer=FakeClient(),
        classes=("abilities", "detachment_rules"),
    )
    for record in records(out, "abilities/candidates.json"):
        AbilitySummary.model_validate(record)
    for record in records(out, "detachment-rules/candidates.json"):
        DetachmentRuleSummary.model_validate(record)


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
