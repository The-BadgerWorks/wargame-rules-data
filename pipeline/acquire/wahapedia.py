# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented detail-source acquisition (task
# T056): retrieval of the CSV export into work/, BOM-aware, with the same SourceAcquisition
# recording and declared_edition_code from WGC_DETAIL_EDITION (FR-003, FR-005).
# AI-Assisted: Claude Code (model: claude-opus-5) - Refuse an unset WGC_DETAIL_SOURCE_URL before
# it is interpreted as a relative path (004 T075 follow-up): an empty location resolved to the
# working directory and reported the first absent export file as an FR-008 partial export.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Added check_table_coverage
# (SRC-TABLE-MISSING, 009 tasks T027/T028, FR-018) and Detachment_abilities.csv to EXPORT_FILES
# (FR-019 parity restoration -- curate/assemble.py already consumed it when html mode supplied
# it; this closes the csv-mode gap the same file's own comment used to explain away).
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Added the export-timestamp short-circuit
# (009 rung R05, T090/T091/T092/T093, FR-030/FR-031/FR-032): `Last_update.csv` joins
# `EXPORT_FILES`, is fetched/read on its own ahead of the rest, and its one-way digest is
# compared against `state/wahapedia-export-digest.json`. The short-circuit is opt-in via the new
# `state_path` parameter -- `None` (every existing caller, including `run_build` through
# `acquire_detail`) is a total no-op, byte-for-byte the prior behaviour, which is what keeps this
# addition from ever silently handing a live build a partial export. A future rung's own job,
# flagged as unresolved by `tasks.md`'s own Phase 7 note, is deciding which caller opts in and
# how a skip composes with a full build; this rung delivers the mechanism and proves it correct
# in isolation, never wires it into `run_build`.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - R05-fix (gate on PR #30, items 1/2/4/5):
# `Last_update.csv` is now excluded from `content_fingerprint`/`acquisition_id` by
# `_corpus_payloads` -- the one place that decides what the corpus is, so a republish with no
# rules change no longer moves the authoritative signal. `_save_export_digest` no longer runs
# inside acquisition -- a caller that opted in now persists `ExportDigestState` itself, only
# after its own downstream work succeeds (`save_export_digest_state`, `export_digest_state_for`).
# The persisted state now carries the source identity the digest was taken under, checked before
# the short-circuit may fire, and a state file that cannot be parsed as a JSON object raises the
# mapped `ExportStateCorrupt` instead of an unmapped traceback.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - R05-fix2 item 3 (gate on PR #30):
# `_corpus_payloads`'s probe exclusion now matches by `Path(name).stem` rather than the exact
# string `"Last_update.csv"`, so it recognises the fixture adapter's own spelling (`"Last_update"`,
# no suffix) too -- plumbed into `acquire_from_fixtures` via its new `corpus_filter` parameter
# (`pipeline/acquire/fixtures.py`), the one place that adapter now excludes anything. Before this
# fix, `acquire_from_fixtures` fingerprinted every loaded payload unconditionally, so under
# `--fixtures` the probe WAS corpus in every `fixtures/detection/*` set, even though the live path
# already excluded it.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - R05-fix2 item 2 (gate on PR #30): an
# UNCHANGED acquisition now carries the PREVIOUS acquisition's own content fingerprint forward
# (`ExportDigestState.content_fingerprint`, persisted alongside `digest`) rather than
# fingerprinting the near-empty payload set the short-circuit actually fetched (just the probe).
# Before this fix, `content_fingerprint([])`'s constant -- the SAME value on every source, every
# run -- was recorded as both the acquisition's own `content_fingerprint` and, via its first 8
# hex characters, its `acquisition_id`, on every UNCHANGED acquisition.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - R05-fix2 item 4 (gate on PR #30):
# `coverage["csv_files"]` counted every file a run touched, probe included, while the content
# fingerprint excluded it -- the two figures described different sets under the same run.
# `csv_files` keeps its original meaning; a new `coverage["corpus_files"]` names what the
# fingerprint actually covers, so a reader cannot mistake one for the other.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 009 rung R06a (T095/T096/T100/T101,
# FR-033): clarified `acquire_wahapedia`'s own docstring so a reader does not repeat this rung's
# own false start -- the `del carried_forward_slugs` a few lines below stays correct as written;
# the silent-discard fix belongs in `pipeline/acquire/detail_source.py::resolve_carried_forward`,
# which is where a declared slug and the acquired payloads are both already in scope. No
# behaviour in this file changed.
"""Acquire the datasheet-detail source: the CSV export, into ``work/``.

Three things are worth stating plainly.

**The export lands in `work/` and nowhere else, with one documented exception.** `work/` is
gitignored, emptied at the start of every command that writes to it and again in a `finally`
(FR-010), and the records handed downstream are the parsed ones, not the files. The exception is
`state/wahapedia-export-digest.json`, written **only** by :func:`save_export_digest_state` —
never called from inside this module, only exposed for a caller that both opted into the
short-circuit (passed a real ``state_path``) and completed its own downstream work successfully.
This is not corpus data: it is a one-way digest of `Last_update.csv` plus the source identity
(``source_base_url``, ``declared_edition_code``, ``mode``) it was taken under, plus the content
fingerprint the acquisition that recorded it already computed (R05-fix2 item 2) — kept for
deciding whether next run's fetch can be skipped, and, when it is, what fingerprint an unchanged
corpus should report instead of an empty one.

**The declared edition is configuration, not inference** (FR-005). The export is 10th Edition
today and the points source is 11th, which is why hybrid pairing is the normal case at launch
rather than an edge case (research §0.1). When the export moves to 11th, the adoption is a
variable change — and no published snapshot is altered or invalidated by it (FR-061). Sniffing
the edition out of the data would make that a code change and, worse, would make it silent.

**The publisher's own change marker is a convenience, never evidence** (FR-030). ``Last_update
.csv`` is fetched/read like any other export file — `_read_local`/`_fetch_remote`'s all-or-nothing
guarantee covers it exactly as it covers every other table (FR-032) — and when ``state_path`` is
given, its one-way digest AND the source identity it was taken under are compared against the
last recorded state *before* the rest of the export is retrieved (R05-fix item 5); either
mismatching means "no comparable prior", never an error. A match short-circuits the remaining
fetch and raises ``SRC-EXPORT-UNCHANGED``; a mismatch (or no prior state) fetches everything and
the existing :func:`~pipeline.acquire.fixtures.content_fingerprint` — computed, as always, over
whatever was actually retrieved, and always excluding the probe itself (:func:`_corpus_payloads`,
R05-fix item 1) — is what a caller must trust, never the digest comparison alone. The
short-circuit sits in front of that fingerprint; nothing here lets it sit over it.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Final
from urllib.parse import unquote, urlparse

from pipeline.acquire.fixtures import FixturePayload, acquire_from_fixtures, content_fingerprint
from pipeline.acquire.http import (
    AcquisitionError,
    PoliteClient,
    SourceUnreachable,
)
from pipeline.build.canonical_json import write_tree_file
from pipeline.config import PipelineConfig
from pipeline.models.findings import Finding
from pipeline.models.source import AcquisitionOutcome, SourceAcquisition, SourceKey
from pipeline.parse.wahapedia_csv import CsvReadResult
from pipeline.report.catalogue import build_finding
from pipeline.workspace import work_dir

#: The export files the pipeline reads. Listed rather than discovered, because a file appearing
#: or disappearing upstream should be a visible failure here rather than a quiet change in what
#: the snapshot was built from. Files carrying only rules text — stratagems — are absent by
#: design: they are read for structural facts only, and nothing in this feature needs one
#: (research D8). ``Detachment_abilities.csv`` (009 task T028, FR-019) is the one exception: it is
#: read for the STRUCTURAL fact of which rule names accompany a detachment, exactly as
#: ``Datasheets_abilities.csv`` already is for datasheets — an acquisition-list change restoring
#: parity with the html arm, explicitly not a coverage expansion (FR-024's no-expansion rule; see
#: `curate/assemble.py::_source_detachment_rules`, which already consumes this file when present
#: and previously only saw it under `html` mode). ``Last_update.csv`` (009 task T090, FR-030) is
#: the newest addition: read by nothing downstream (`plan.md` finding 9 — greenfield), it carries
#: only the publisher's own whole-export change marker and exists here purely so the short-circuit
#: below is bound by the same all-or-nothing fetch guarantee (FR-032) as every other table.
EXPORT_FILES: Final[tuple[str, ...]] = (
    "Abilities.csv",
    "Datasheets.csv",
    "Datasheets_abilities.csv",
    "Datasheets_keywords.csv",
    "Datasheets_leader.csv",
    "Datasheets_models.csv",
    "Datasheets_models_cost.csv",
    "Datasheets_options.csv",
    "Datasheets_unit_composition.csv",
    "Datasheets_wargear.csv",
    "Detachment_abilities.csv",
    "Detachments.csv",
    "Enhancements.csv",
    "Factions.csv",
    "Last_update.csv",
    "Source.csv",
)

#: The one file the short-circuit probes ahead of the rest (T090). A module-level name rather
#: than a literal repeated at each call site, so the "fetched first, on its own" contract is one
#: fact instead of several strings that could drift apart.
LAST_UPDATE_FILE: Final = "Last_update.csv"

#: ``state/``'s new file for this rung (T090, state/README.md's one-way-digest-only rule). Holds
#: a ``digest`` — sha256 hex over ``Last_update.csv``'s own text, never the text itself — plus
#: the source identity it was taken under (R05-fix item 5). Seeded empty (``{}``): no prior run
#: has ever reached the short-circuit.
EXPORT_DIGEST_STATE_RELATIVE_PATH: Final = "state/wahapedia-export-digest.json"


class ExportStateCorrupt(AcquisitionError):
    """``state_path`` exists but is not a JSON object (R05-fix item 4).

    This pipeline is the only writer of this file — a run that reaches it and finds something
    else is evidence the file was hand-edited, truncated, or overwritten by something outside the
    contract, never a fact to route around. **Fail closed**: raised as a mapped error the CLI can
    turn into the right exit code, never swallowed into "no prior" and never left to crash with
    an unmapped traceback. The short-circuit still does not fire either way — the difference is
    that a missing file is silently unremarkable while a corrupt one is not.
    """

    finding_code = "SRC-STATE-CORRUPT"


def _one_way_export_digest(text: str) -> str:
    """sha256 hex over ``Last_update.csv``'s text — never the text itself.

    ``state/README.md`` permits state files to hold one-way digests and hashes only; a raw
    publisher timestamp is retained publisher data, a Tier 1 defect in this project regardless of
    where it turns up. A digest compares for equality exactly as well as the timestamp does,
    which is the only operation a short-circuit needs (``research.md``, "Explicitly not research
    questions").
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class ExportDigestState:
    """The short-circuit's persisted state: a digest, the identity it was taken under, and the
    content fingerprint it authorises a caller to carry forward.

    R05-fix item 5: comparing a digest across differently-configured sources (a different
    ``source_base_url``, a different declared detail edition, or a different acquisition mode)
    would let one configuration's "unchanged" wrongly skip another's fetch. Recording the
    identity here, and requiring it to match before :func:`acquire_wahapedia` may short-circuit,
    is what closes that. A mismatch is never an error — see that function's own docstring — it
    simply means there is nothing comparable to compare against.

    R05-fix2 item 2: ``content_fingerprint`` is the corpus fingerprint the acquisition that
    *produced* this state itself reported — never recomputed from the near-empty payload set a
    short-circuited run actually fetches (just the probe). It is what lets a short-circuited
    acquisition report "the same corpus as last time" instead of an empty one.
    """

    __slots__ = (
        "digest",
        "content_fingerprint",
        "source_base_url",
        "declared_edition_code",
        "mode",
    )

    def __init__(
        self,
        *,
        digest: str,
        content_fingerprint: str,
        source_base_url: str,
        declared_edition_code: str,
        mode: str,
    ) -> None:
        self.digest = digest
        self.content_fingerprint = content_fingerprint
        self.source_base_url = source_base_url
        self.declared_edition_code = declared_edition_code
        self.mode = mode

    @property
    def identity(self) -> tuple[str, str, str]:
        """The three fields a caller's current configuration must match for the digest above to
        be comparable at all."""
        return (self.source_base_url, self.declared_edition_code, self.mode)


def load_export_digest_state(path: Path) -> ExportDigestState | None:
    """The state the last successful, opted-in run recorded, or ``None``.

    ``None`` covers two different, both entirely ordinary, facts: the file does not exist yet (no
    prior run has ever reached the short-circuit), and the file exists but is the seeded-empty
    ``{}`` (same fact, written down explicitly instead of left absent). Either way the caller's
    only correct move is to fetch — there is nothing to compare against.

    A file that exists and is **not** valid JSON, or is valid JSON that is not an object, is a
    third, different fact — the tracked state itself is broken — and is raised as
    :class:`ExportStateCorrupt` rather than folded into the same ``None`` (R05-fix item 4,
    "fail closed": a state file that cannot be read must never be treated as silently absent).

    R05-fix2 item 2: a state that carries a ``digest`` but no ``content_fingerprint`` — the
    seeded-empty ``{}``, or a state written by code older than this fix — has nothing safe for a
    short-circuited acquisition to carry forward, so it is treated the same as no prior state at
    all (``None``), never as license to report an empty-corpus fingerprint.
    """
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    try:
        raw = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ExportStateCorrupt(f"{path} does not hold valid JSON: {exc}") from exc
    if not isinstance(raw, dict):
        raise ExportStateCorrupt(f"{path} does not hold a JSON object (got {type(raw).__name__})")
    digest = raw.get("digest")
    content_fingerprint_value = raw.get("content_fingerprint")
    if not digest or not content_fingerprint_value:
        return None  # the seeded-empty {} state, or a state written before either field existed
    return ExportDigestState(
        digest=str(digest),
        content_fingerprint=str(content_fingerprint_value),
        source_base_url=str(raw.get("source_base_url", "")),
        declared_edition_code=str(raw.get("declared_edition_code", "")),
        mode=str(raw.get("mode", "")),
    )


def save_export_digest_state(path: Path, state: ExportDigestState) -> None:
    """Persist ``state`` through the same canonical-JSON writer every other state file uses.

    Never called from inside :func:`acquire_wahapedia` (R05-fix item 2) — acquisition alone does
    not know whether the caller's own downstream work will succeed, and advancing this file on an
    acquisition that turned out to feed a failed run is exactly the hazard that let a genuinely
    changed export go un-re-fetched forever. Call this only after the whole run it belongs to has
    succeeded, the same way ``detect.yml`` writes ``state/detection-digest.json`` only after a
    successful sweep.
    """
    write_tree_file(
        path,
        {
            "digest": state.digest,
            "content_fingerprint": state.content_fingerprint,
            "source_base_url": state.source_base_url,
            "declared_edition_code": state.declared_edition_code,
            "mode": state.mode,
        },
    )


def export_digest_state_for(
    config: PipelineConfig,
    acquisition: SourceAcquisition,
    payloads: Sequence[FixturePayload],
) -> ExportDigestState | None:
    """The state worth persisting after a completed, successful acquisition, or ``None``.

    ``None`` when ``payloads`` carries no :data:`LAST_UPDATE_FILE` entry — a fixture-driven run
    (which never reaches the probe at all) or any acquisition that did not go through this
    module. A caller calls this, then :func:`save_export_digest_state`, only once its own
    downstream work has succeeded (R05-fix item 2) — never from inside acquisition itself.

    R05-fix2 item 2: ``content_fingerprint`` carries ``acquisition``'s own, already-computed
    corpus fingerprint forward — never recomputed here — so a future short-circuited acquisition
    that matches this state can report "the same corpus as this one had" instead of fingerprinting
    the near-empty payload set it actually fetches.
    """
    probe = next((payload for payload in payloads if payload.name == LAST_UPDATE_FILE), None)
    if probe is None:
        return None
    return ExportDigestState(
        digest=_one_way_export_digest(probe.text),
        content_fingerprint=acquisition.content_fingerprint.removeprefix("sha256:"),
        source_base_url=acquisition.source_base_url,
        declared_edition_code=acquisition.declared_edition_code,
        mode=config.detail_acquisition_mode.value,
    )


#: :data:`LAST_UPDATE_FILE`'s own name, normalised to its stem. The live path names the probe's
#: payload ``"Last_update.csv"`` (`_read_local`/`_fetch_remote` keep the file's own name); the
#: fixture adapter names it ``"Last_update"`` (`load_fixture_payloads` uses ``Path.stem`` for
#: every payload). R05-fix2 item 3: comparing by stem is the ONE normalisation both spellings
#: resolve to, so there is exactly one place this decision is made rather than two that can
#: silently drift apart -- which is exactly what happened before this fix: `_corpus_payloads`
#: excluded the exact string ``"Last_update.csv"``, which the fixture adapter's payload never is,
#: so under ``--fixtures`` the probe was corpus in every `fixtures/detection/*` set.
_PROBE_STEM: Final = Path(LAST_UPDATE_FILE).stem


def _is_probe(payload: FixturePayload) -> bool:
    """Whether ``payload`` is the export-timestamp probe, regardless of which adapter read it."""
    return Path(payload.name).stem == _PROBE_STEM


#: The files that count as the export's own content — what may move the content fingerprint and
#: the acquisition_id derived from it. The **only** place that decision is made (R05-fix item 1;
#: made spelling-independent by R05-fix2 item 3): :data:`LAST_UPDATE_FILE` is fetched like any
#: other table (the all-or-nothing guarantee still covers it) but is never corpus, so a bare
#: regeneration timestamp can never masquerade as a rules change. A file added to
#: :data:`EXPORT_FILES` later is corpus by default and has to be excluded here deliberately, the
#: same way this one was -- exactly the property that was missing before this fix. Passed to
#: :func:`~pipeline.acquire.fixtures.acquire_from_fixtures` as its ``corpus_filter`` (R05-fix2
#: item 3) so the SAME function decides this under ``--fixtures`` too, rather than that module
#: reimplementing the exclusion by name.
def _corpus_payloads(payloads: Sequence[FixturePayload]) -> list[FixturePayload]:
    return [payload for payload in payloads if not _is_probe(payload)]


def _local_directory(location: str) -> Path | None:
    """The local directory ``location`` names, or ``None`` when it names an HTTP resource.

    A curator running against a locally held export should exercise the same code path as CI
    does against the hosted one — the alternative is a second acquisition path that only ever
    runs on a laptop, which is exactly what contract §1 rules out.
    """
    parsed = urlparse(location)
    if parsed.scheme == "file":
        return Path(unquote(parsed.netloc + parsed.path))
    if parsed.scheme in {"http", "https"}:
        return None
    return Path(location)


def _read_local(directory: Path, names: Sequence[str] = EXPORT_FILES) -> list[FixturePayload]:
    """Read ``names`` from ``directory``, in order, failing whole on the first miss (FR-032).

    ``names`` defaults to the full :data:`EXPORT_FILES` list — every existing call keeps its
    exact prior behaviour — but the short-circuit calls this twice, once for
    :data:`LAST_UPDATE_FILE` alone and once for the rest, so it can decide between the two reads
    without weakening the all-or-nothing guarantee either read makes on its own.
    """
    if not directory.is_dir():
        raise SourceUnreachable(
            f"the detail source's export directory does not exist: {directory} "
            "(WGC_DETAIL_SOURCE_URL)"
        )
    payloads: list[FixturePayload] = []
    for name in names:
        path = directory / name
        if not path.is_file():
            raise SourceUnreachable(
                f"the detail source's export is missing {name}; a partial export is a failed "
                "acquisition rather than a smaller snapshot (FR-008)"
            )
        payloads.append(FixturePayload(name=name, text=path.read_text(encoding="utf-8-sig")))
    return payloads


def _fetch_remote(
    client: PoliteClient, base: str, names: Sequence[str] = EXPORT_FILES
) -> list[FixturePayload]:
    """Fetch ``names`` from ``base``, in order, failing whole on the first miss (FR-032).

    Same ``names`` parameter and the same reason as :func:`_read_local`'s.
    """
    payloads: list[FixturePayload] = []
    for name in names:
        response = client.get(f"{base.rstrip('/')}/{name}")
        if response.status_code != 200:
            raise SourceUnreachable(
                f"the detail source responded {response.status_code} for {name}; a partial "
                "export is a failed acquisition (FR-008)"
            )
        # The export is UTF-8 with a BOM; decoding it away here means no parser downstream has
        # to know that, and a fixture may carry a BOM exactly as the real file does.
        payloads.append(FixturePayload(name=name, text=response.content.decode("utf-8-sig")))
    return payloads


#: Every table but the change marker itself — what the short-circuit still has to fetch when it
#: does not skip. Computed once at import time rather than filtered per call.
_REMAINING_EXPORT_FILES: Final[tuple[str, ...]] = tuple(
    name for name in EXPORT_FILES if name != LAST_UPDATE_FILE
)


def acquire_wahapedia(
    config: PipelineConfig,
    *,
    fixtures_dir: Path | None = None,
    offline: bool = False,
    client: PoliteClient | None = None,
    retrieved_at: datetime | None = None,
    workspace: Path | None = None,
    carried_forward_slugs: frozenset[str] = frozenset(),
    state_path: Path | None = None,
) -> tuple[SourceAcquisition, list[FixturePayload]]:
    """Acquire the detail-source export.

    When ``workspace`` is given the retrieved files are written into it — that is ``work/``, and
    it is the only place they are ever written.

    ``carried_forward_slugs`` is accepted and unused, on the same terms
    :func:`pipeline.acquire.detail_source.read_export_payloads` already accepts and ignores
    ``edition_code``: the signature is shared with the html arm so a caller never learns which
    mode ran (008 FR-024). The bulk export has no per-faction page to fail partway through — it
    is one file or none — so there is genuinely nothing HERE for a carry-forward declaration to
    apply to, and the ``del`` below stays correct on that count.

    009 rung R06a (T095/T096/T100/T101, FR-033): that is NOT the same claim as "a declaration
    under this arm may be dropped silently" — a claim this docstring used to make no comment on,
    and `tasks.md`'s T100 (written before rung R01b restructured this area) once located the fix
    for that right here. It does not belong here: this function has no ``declared_slugs`` vs.
    ``fetched`` diff to run, because a payload's ``name`` at this layer is a file name
    (``Datasheets.csv``), never a faction slug — the same reasoning
    :class:`pipeline.acquire.detail_source.CarriedForwardOutcome` gives for its own ``carried``
    field. Visibility lives one level up, in
    :func:`pipeline.acquire.detail_source.resolve_carried_forward`, which is where
    ``declared_slugs`` and the acquired payloads are both already in scope — a declaration is
    now reported ``unused`` (never dropped) there, under this arm exactly as under any arm but
    ``html``. This function's own ``del`` remains a true no-op on an unused parameter, not the
    place the silent discard used to happen.

    ``state_path`` (009 rung R05, T090; identity check added R05-fix item 5) is the
    export-timestamp short-circuit's own opt-in switch, pointed at
    :data:`EXPORT_DIGEST_STATE_RELATIVE_PATH`. **``None`` — the default, and every call this rung
    leaves unchanged, including every call `run_build` makes — is a total no-op**:
    :data:`LAST_UPDATE_FILE` is still fetched (it is simply one more name in :data:`EXPORT_FILES`
    now), but nothing is ever skipped and the fingerprint is computed over the complete export
    exactly as before this rung. When a caller opts in by passing a real path:
    :data:`LAST_UPDATE_FILE` is read first, on its own; if its digest matches the digest
    :func:`load_export_digest_state` reads back from ``state_path`` **and** the state's recorded
    identity (``source_base_url``, ``declared_edition_code``, ``mode``) matches this call's own —
    a mismatch on either is "no comparable prior", not an error — the remaining
    :data:`_REMAINING_EXPORT_FILES` are never requested, ``outcome`` is
    :attr:`~pipeline.models.source.AcquisitionOutcome.UNCHANGED`, and the returned ``findings``
    carry ``SRC-EXPORT-UNCHANGED`` (FR-031) — otherwise every file is fetched exactly as it always
    was, and :func:`~pipeline.acquire.fixtures.content_fingerprint` runs over that complete,
    freshly-fetched set, excluding the probe either way (:func:`_corpus_payloads`, R05-fix item
    1). **This function itself never writes ``state_path``** (R05-fix item 2): a caller that wants
    the next call to be able to skip calls :func:`export_digest_state_for` and
    :func:`save_export_digest_state` itself, only once its own downstream work has succeeded —
    acquiring a genuinely new export and then advancing the state regardless of what happened
    next is the exact hazard that would leave the changed export un-re-fetched forever.

    A fixture run (``fixtures_dir``) never reaches any of this — :func:`acquire_from_fixtures`
    returns before ``state_path`` is even inspected, exactly as it always has.
    """
    del carried_forward_slugs
    if fixtures_dir is not None:
        # R05-fix2 item 3: `corpus_filter=_corpus_payloads` so the fixture adapter excludes the
        # probe on the SAME predicate the live path below uses, rather than never excluding it at
        # all -- see `_corpus_payloads`'s own docstring.
        return acquire_from_fixtures(
            fixtures_dir,
            SourceKey.WAHAPEDIA,
            config,
            retrieved_at=retrieved_at,
            corpus_filter=_corpus_payloads,
        )

    # Refused here rather than interpreted: an empty location is a relative path, and a relative
    # path is the working directory. See `PipelineConfig.require_detail_source`.
    location = config.require_detail_source()
    directory = _local_directory(location)
    request_count = 0
    outcome = AcquisitionOutcome.OK
    findings: tuple[Finding, ...] = ()
    coverage: dict[str, int]

    prior_state = load_export_digest_state(state_path) if state_path is not None else None
    current_identity = (location, config.detail_edition, config.detail_acquisition_mode.value)
    owned = client is None
    active: PoliteClient | None = None
    try:
        if directory is not None:
            last_update = _read_local(directory, (LAST_UPDATE_FILE,))[0]
        else:
            active = client or PoliteClient(config, offline=offline)
            last_update = _fetch_remote(active, location, (LAST_UPDATE_FILE,))[0]
            request_count = active.request_count

        fresh_digest = _one_way_export_digest(last_update.text)
        # T088/FR-030's central guarantee lives in this one condition: the short-circuit fires
        # ONLY when a caller opted in (`state_path` given) AND a prior state exists AND its
        # recorded identity matches this call's own (R05-fix item 5) AND the digest matches.
        # Every other combination — no `state_path`, first run, a moved digest, or a matching
        # digest recorded under a different source configuration — falls through to the full
        # fetch below, where the content fingerprint is computed over real, current bytes exactly
        # as it always has been. The digest is never asked to stand in for that fingerprint; it
        # only ever decides whether the fingerprint's own inputs are worth re-requesting.
        short_circuit = (
            state_path is not None
            and prior_state is not None
            and prior_state.identity == current_identity
            and fresh_digest == prior_state.digest
        )
        if short_circuit:
            payloads = [last_update]
            outcome = AcquisitionOutcome.UNCHANGED
            findings = (build_finding("SRC-EXPORT-UNCHANGED", detail={"table": LAST_UPDATE_FILE}),)
        else:
            if directory is not None:
                rest = _read_local(directory, _REMAINING_EXPORT_FILES)
            else:
                assert active is not None  # narrows for mypy; set above whenever directory is None
                rest = _fetch_remote(active, location, _REMAINING_EXPORT_FILES)
                request_count = active.request_count
            payloads = [last_update, *rest]

        # R05-fix item 2: state_path is READ above (to decide the short-circuit) but never
        # WRITTEN here -- see save_export_digest_state's own docstring for why that is now the
        # caller's job, and only after its own downstream work succeeds.
    except AcquisitionError:
        raise
    finally:
        if owned and active is not None:
            active.close()

    if workspace is not None:
        target = workspace / "wahapedia"
        target.mkdir(parents=True, exist_ok=True)
        for payload in payloads:
            (target / payload.name).write_text(payload.text, encoding="utf-8", newline="\n")

    moment = (retrieved_at or datetime.now(UTC)).astimezone(UTC)
    corpus = _corpus_payloads(payloads)
    if outcome is AcquisitionOutcome.UNCHANGED:
        # R05-fix2 item 2: the short-circuit only fetched the probe, so `corpus` is empty here --
        # `content_fingerprint(corpus)` would return the constant every empty input hashes to,
        # reported as if the corpus itself were empty, on every UNCHANGED run against every
        # source. `short_circuit`'s own condition already required `prior_state` to be non-None
        # and identity-matched, so the fingerprint IT recorded is exactly what this unchanged
        # corpus was last measured to be -- carried forward rather than recomputed from bytes
        # this run never fetched.
        assert prior_state is not None  # narrows for mypy; `short_circuit` already proved it
        fingerprint = prior_state.content_fingerprint
    else:
        # R05-fix item 1: the probe is fetched (above) but never counted as corpus -- see
        # _corpus_payloads's own docstring for why this is the one place that decision is made.
        fingerprint = content_fingerprint(corpus)
    # R05-fix2 item 4: `csv_files` keeps its original meaning -- every file THIS RUN touched,
    # probe included, which is what T093's `csv_files_total` comparison below still needs -- and
    # `corpus_files` is added alongside it, naming what the fingerprint actually covers, so a
    # reader cannot mistake one count for the other the way a single `csv_files` key invited.
    coverage = {"csv_files": len(payloads), "corpus_files": len(corpus)}
    if outcome is AcquisitionOutcome.UNCHANGED:
        # T093: the surface reduction the short-circuit buys, recorded rather than merely
        # implied by a smaller `csv_files` count -- a curator sees both numbers without having
        # to know EXPORT_FILES's own length.
        coverage["csv_files_total"] = len(EXPORT_FILES)

    acquisition = SourceAcquisition(
        acquisition_id=f"wahapedia-{moment.strftime('%Y%m%dT%H%M%SZ')}-{fingerprint[:8]}",
        source_key=SourceKey.WAHAPEDIA,
        source_base_url=location,
        declared_edition_code=config.detail_edition,
        retrieved_at=moment.isoformat().replace("+00:00", "Z"),
        content_fingerprint=f"sha256:{fingerprint}",
        coverage=coverage,
        request_count=request_count,
        request_interval_ms=config.request_interval_ms,
        outcome=outcome,
        findings=findings,
    )
    return acquisition, payloads


def default_workspace() -> Path:
    """The ``work/`` directory the export lands in when no other is given."""
    return work_dir()


def check_table_coverage(
    detail: Mapping[str, CsvReadResult], *, consumed_tables: Sequence[str]
) -> list[Finding]:
    """``SRC-TABLE-MISSING`` (009 FR-018, rule 3): a table the build consumes is absent or empty.

    Asserted against ``detail`` — the parsed reader output of an actual acquisition
    (:func:`pipeline.acquire.detail_source.read_detail`'s return shape) — never against a fixture
    directory listing. A file existing on disk (which ``_read_local``'s ``EXPORT_FILES`` sweep
    already guards, by raising :class:`~pipeline.acquire.http.SourceUnreachable`) proves nothing
    about whether the acquisition actually produced usable rows from it; this catches the case
    that check misses, a table present but genuinely empty.

    ``consumed_tables`` is deliberately a parameter rather than a hardcoded list: which tables
    the build actually indexes into varies by stage and by arm (``Detachment_abilities.csv`` is
    html-only until T028's own change; the derived equipment table is Phase 5's), so the caller
    states its own scope rather than this function guessing it.
    """
    return [
        build_finding("SRC-TABLE-MISSING", detail={"table": table})
        for table in consumed_tables
        if not (result := detail.get(table)) or not result.rows
    ]
