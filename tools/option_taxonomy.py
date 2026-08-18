#!/usr/bin/env python3
# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the option-row taxonomy classifier
# (006 task T001): acquire the detail source in the configured mode into an ephemeral work/, run
# every option row through the pipeline's own parse path, classify each unparsed row against
# research D1b's thirteen classes and its cross-cutting features, measure D1d's two silent-failure
# classes over the rows that DO parse, and write counts to reports/option-taxonomy/<date>.md —
# retaining no source text anywhere, exactly as tools/churn_dry_run.py retains no mechanic wording
# (006 risk R-A).
"""Re-derive the unparsed-option taxonomy against a corpus, before a production is written.

`006`'s whole grammar plan is sized off research D1b, and D1b was measured over a **cached ~81 %
sample** of the published corpus (24 of 30 faction pages, retrieved during the `004`/`005`
campaign). That is risk **R-A**: the *shape distribution* is what the design rests on and it is
stable at that sample size, but the absolute counts are approximate and the ordering the build
plan follows — one distributive verb production clearing ≈49.6 % alone, four productions covering
≈68 % — has never been confirmed against a corpus the candidate itself acquired.

This tool confirms it, or contradicts it::

    python tools/option_taxonomy.py                                      # live, configured source
    python tools/option_taxonomy.py --fixtures fixtures/minimal --offline  # rehearsal, no network

Four properties, each of which is why a line of this file exists:

* **It uses the pipeline's own parse path.** Rows come from
  :func:`pipeline.acquire.detail_source.read_detail` — which in ``html`` mode is
  :func:`pipeline.parse.wahapedia_html_dom.parse_faction_page` over each acquired page, reading
  each card's ``options`` — and every row is resolved by
  :func:`pipeline.parse.options_grammar.parse_row`. A classifier with its own idea of what fails
  to parse would measure itself.
* **The acquired text is discarded.** It lands in a workspace emptied on exit, whatever happens,
  and nothing but counts leaves this process.
* **No source text reaches the report.** Not a sentence, not a fragment, not an item name. The
  report carries class counts and nothing else, which is the same standard research D1 held
  itself to and the reason that document carries frequency tables and no sentences.
* **It writes nothing outside ``reports/option-taxonomy/``.** It is a measurement, never an edit:
  it does not touch ``data/``, ``curation/``, or ``state/``.

**Classification is disjoint and ordered.** Each unparsed row lands in exactly one class — the
first rule that matches, in the fixed order below — so the per-class counts sum to the residual
and a production can be sized off one number. The *features* table is deliberately the opposite:
its rows overlap, because "carries a multi-item granted bundle" and "is a distributive replace"
are properties of the same sentence and both bear on what the grammar must carry.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

from pipeline.acquire.detail_source import acquire_detail, read_detail
from pipeline.acquire.http import AcquisitionError
from pipeline.config import (
    ConfigError,
    DetailAcquisitionMode,
    PipelineConfig,
    load_config,
    repo_root,
)
from pipeline.curate.prior import previous_published_version, read_curated_tree
from pipeline.exit_codes import ExitCode
from pipeline.models.curated import CuratedSnapshot, WargearOptionState
from pipeline.parse.composition_grammar import pre_pass
from pipeline.parse.options_grammar import parse_row, split_sublist
from pipeline.workspace import workspace

PROG: Final = "option_taxonomy.py"

#: Where the measurement lands. Its own directory, never ``reports/candidate/``: this is not a
#: run report and must not be mistaken for one by a reviewer or by the publish gate.
REPORTS_DIR: Final = Path("reports") / "option-taxonomy"

_OPTIONS_TABLE: Final = "Datasheets_options.csv"
_DATASHEETS_TABLE: Final = "Datasheets.csv"

_I: Final = re.IGNORECASE


@dataclass(frozen=True, slots=True)
class ClassRule:
    """One disjoint taxonomy class: the first rule that matches owns the row."""

    key: str
    label: str
    stem: re.Pattern[str] | None = None
    """Matched against the pre-passed stem clause."""

    absent: re.Pattern[str] | None = None
    """A pattern that must NOT be present for this rule to own the row."""

    def matches(self, stem: str) -> bool:
        if self.stem is not None and self.stem.search(stem) is None:
            return False
        return not (self.absent is not None and self.absent.search(stem) is not None)


#: The distributive replace verb — research D1b class 1, ≈49.6 % of the measured residual on its
#: own and the single highest-yield production in the feature (006 task T016).
_DISTRIBUTIVE_REPLACE: Final = re.compile(r"can each have\b.*\breplaced with\b", _I)

#: The two verbs the `004` grammar already carries. A row matching one of these failed on its
#: *head*, which is a different production to write than a row that failed on its verb.
_BUILT_VERB: Final = re.compile(r"can be (?:replaced|equipped) with\b", _I)

#: Research D1b's thirteen classes, in the fixed order they are tried. The order encodes the
#: taxonomy's own nesting: the distributive-replace family is separated out before the generic
#: "verb already built" class can claim its members, and the two extractor-misfiling classes (6
#: and 11) are tried first of all, because they are not option sentences at all and counting them
#: as grammar gaps would size a production against a bug (research D1c.4, 006 task T022).
_CLASSES: Final[tuple[ClassRule, ...]] = (
    ClassRule(
        "6",
        "A default-equipment sentence misfiled into the options block (extractor bug)",
        stem=re.compile(r"\bis equipped with\s*:", _I),
        absent=re.compile(r"\bcan\b", _I),
    ),
    ClassRule("1c", "Distributive replace, scoped subset with a max", stem=None),
    ClassRule("1d", "Distributive replace, ratio head with a nested subset max", stem=None),
    ClassRule("1e", "Distributive replace, whole-unit head", stem=None),
    ClassRule("1a", "Distributive replace, head `Any number of ... models`", stem=None),
    ClassRule("1b", "Distributive replace, head names a model type", stem=None),
    ClassRule("1f", "Distributive replace, other head", stem=None),
    ClassRule(
        "8",
        "Item-subject passive — `... can each be replaced with`",
        stem=re.compile(r"can each be replaced with\b", _I),
    ),
    ClassRule(
        "3",
        "Distributive equip verb — `can each be equipped with`",
        stem=re.compile(r"can each be equipped with\b", _I),
    ),
    ClassRule(
        "7",
        "Active-voice replace, distributive — `can each replace ... with`",
        stem=re.compile(r"can each replace\b", _I),
    ),
    ClassRule(
        "5",
        "Non-distributive `can have ... replaced with`",
        stem=re.compile(r"can have\b.*\breplaced with\b", _I),
    ),
    ClassRule(
        "4",
        "Active-voice replace, per-unit — `can replace its/their ... with`",
        stem=re.compile(r"can replace\b.*\bwith\b", _I),
    ),
    ClassRule("2", "Head unknown, verb already built", stem=_BUILT_VERB),
    ClassRule(
        "10",
        "Pure grant, no replacement — `... can have INT [ITEM]`",
        stem=re.compile(r"\bcan (?:each )?have\b", _I),
        absent=re.compile(r"\breplaced\b", _I),
    ),
    # Ordered ahead of class 11 deliberately. A conditional stem that opens an `li` list —
    # `If this unit has INT or more models:` — carries no clause vocabulary at all, so a
    # short-fragment rule tried first would file a group availability predicate as an extractor
    # bug and hide the one class research D1c.5 says to plan no production for.
    ClassRule(
        "9",
        "Conditional stem opening a list, no verb in the stem",
        stem=re.compile(r"^(?:If|Unless|For every)\b.*:$", _I),
    ),
    ClassRule(
        "12",
        "Upstream typo — a missing `with`, a `must be equipped`",
        stem=re.compile(r"\bmust be equipped\b|\breplaced\b(?!.*\bwith\b)", _I),
    ),
    ClassRule(
        "11",
        "Footnote fragment extracted as its own row (extractor bug)",
        stem=re.compile(r"^[^.]{0,60}\.?$"),
        absent=re.compile(r"\b(?:can|must|equipped|replaced|following)\b", _I),
    ),
    ClassRule("13", "Residual unclassified", stem=None),
)

#: The heads of the distributive-replace family, tried in this order once class 1 is established.
#: They are the four productions 006 tasks T016-T017 build, plus the two that are left to
#: overrides, so the report reads directly as a build order.
_DISTRIBUTIVE_HEADS: Final[tuple[tuple[str, re.Pattern[str]], ...]] = (
    ("1d", re.compile(r"^For every \d+ models?\b.*\bup to \d+\b", _I)),
    ("1c", re.compile(r"^Up to \d+\s+\S", _I)),
    ("1e", re.compile(r"^All models in this unit\b", _I)),
    ("1a", re.compile(r"^Any number of\b.*\bmodels\b", _I)),
    ("1b", re.compile(r"^Any number of\b", _I)),
)

#: The class-1 sub-class keys, resolved by :data:`_DISTRIBUTIVE_HEADS` rather than by a rule in
#: :data:`_CLASSES`. Named as a set so the classifier's skip cannot be spelled as a prefix test.
_DISTRIBUTIVE_FAMILY: Final[frozenset[str]] = frozenset({"1a", "1b", "1c", "1d", "1e", "1f"})

#: Research D1b's cross-cutting features, over the same rows. **Not disjoint** — a single row
#: routinely carries three of them — so these counts do not sum to the residual and are not meant
#: to. Each names a capability the grammar must carry rather than a production it must add.
_FEATURES: Final[tuple[tuple[str, str], ...]] = (
    ("sublist", "carries an `li` sub-list"),
    ("following", "stem ends `one of the following:`"),
    ("multi_replaced", "multi-item REPLACED set (FR-005)"),
    ("multi_granted", "multi-item GRANTED bundle (FR-006)"),
    ("distributive", "distributive `can each` (FR-004, `isPerModel`)"),
    ("scoped_max", "`Up to INT [MODEL]` — an explicit eligibility cap (`eligibleMaxCount`)"),
    ("footnote", "carries a footnote marker inside the stem"),
)

_FOLLOWING: Final = re.compile(r"one of the following\s*:?\s*$", _I)
_DISTRIBUTIVE: Final = re.compile(r"\bcan each\b", _I)
_SCOPED_MAX: Final = re.compile(r"^Up to \d+\s+\S", _I)
_FOOTNOTE: Final = re.compile(r"[*†‡¹²³]")

#: The replaced side of a distributive or passive clause: what sits between the possessive and
#: the replace verb. A conjunction inside it is a multi-item replaced set.
_REPLACED_SIDE: Final = re.compile(
    r"\bhave\s+(?:its|their|this model's|the)\s+(?P<side>.+?)\s+replaced with\b", _I
)

#: A conjunction joining two counted items — `INT [ITEM] and INT [ITEM]` — on the granted side.
#: The leading count is what distinguishes a bundle from an item whose own name contains `and`.
_COUNTED_CONJUNCT: Final = re.compile(r"^\d+\s+.+?\s+and\s+\d+\s+\S", _I)

#: Research D1d's first silent-failure class, over the rows that **do** parse: the whole object
#: clause collapsed into one choice `name`, so the bundle is conflated rather than truncated and
#: the choice ships unlinked (006 task T018 decomposes these without renaming them — the O1
#: Ruling).
_CONFLATED_NAME: Final = re.compile(r"\band\s+\d+\s+\S|\b\S+\s+(?:and|or)\s+\S+", _I)

#: Research D1d's second: a group-level select quantifier in the stem's post-verb remainder,
#: discarded today whenever an `li` list exists, so the group publishes as *pick any number*
#: where the source says *pick up to N* (006 task T019 populates `min_choices`/`max_choices`).
_SELECT_QUANTIFIER: Final = re.compile(
    r"\b(?:up to \d+ of the following|\d+ different\b.*\bfrom the following)", _I
)

#: A deliberately looser probe for the same idea: any ``… of the following`` that is **not** the
#: ``one of the following`` boilerplate. It exists so a measured zero above reads as "this corpus
#: states no group-level select quantifier" rather than as "the strict pattern missed the
#: phrasing" — very different findings for 006 T019, and indistinguishable without it.
_QUANTIFIER_PROBE: Final = re.compile(r"\bof the following\b", _I)
_BOILERPLATE_FOLLOWING: Final = re.compile(r"\bone of the following\b", _I)


def classify(stem: str) -> str:
    """The one class this unparsed stem belongs to, as a research D1b key.

    Disjoint and ordered: the first rule that matches owns the row, so the per-class counts sum
    to the residual exactly.
    """
    if _DISTRIBUTIVE_REPLACE.search(stem) is not None:
        for key, pattern in _DISTRIBUTIVE_HEADS:
            if pattern.search(stem) is not None:
                return key
        return "1f"
    for rule in _CLASSES:
        # The class-1 family is resolved above, by head, and its placeholder rules carry no
        # pattern. `startswith("1")` would also swallow classes 10-13, which is how a taxonomy
        # quietly loses four classes to its own residual bucket.
        if rule.key in _DISTRIBUTIVE_FAMILY:
            continue
        if rule.matches(stem):
            return rule.key
    return "13"


def features_of(stem: str, items: Sequence[str]) -> frozenset[str]:
    """The cross-cutting features this row carries. Overlapping by design."""
    found: set[str] = set()
    if items:
        found.add("sublist")
    if _FOLLOWING.search(stem) is not None:
        found.add("following")
    if _DISTRIBUTIVE.search(stem) is not None:
        found.add("distributive")
    if _SCOPED_MAX.search(stem) is not None:
        found.add("scoped_max")
    if _FOOTNOTE.search(stem) is not None:
        found.add("footnote")

    replaced = _REPLACED_SIDE.search(stem)
    if replaced is not None and " and " in replaced.group("side"):
        found.add("multi_replaced")

    granted = [pre_pass(item, field="option.choice") for item in items]
    if not granted:
        _, remainder = _split_on_verb(stem)
        granted = [remainder] if remainder else []
    if any(_COUNTED_CONJUNCT.match(text) is not None for text in granted):
        found.add("multi_granted")
    return frozenset(found)


def _split_on_verb(stem: str) -> tuple[str, str]:
    """The stem up to its verb phrase, and what follows it. ``("", "")`` when neither verb is in."""
    for phrase in ("can be replaced with", "can be equipped with", "replaced with"):
        index = stem.find(phrase)
        if index >= 0:
            return stem[:index], stem[index + len(phrase) :].strip()
    return "", ""


@dataclass(frozen=True, slots=True)
class FactionTaxonomy:
    """One faction's rows, classified."""

    faction_id: str
    datasheets: int
    datasheets_with_options: int
    rows: int
    unparsed: int
    partial_datasheets: int

    @property
    def ratio(self) -> float:
        return self.unparsed / self.rows if self.rows else 0.0


@dataclass(frozen=True, slots=True)
class TaxonomyReport:
    """The whole measurement: counts, and only counts."""

    generated_at: str
    mode: str
    edition: str
    source: str
    factions: tuple[FactionTaxonomy, ...]
    classes: Mapping[str, int]
    features: Mapping[str, int]
    parsed_conflated_names: int
    parsed_dropped_quantifiers: int
    unparsed_select_quantifiers: int = 0
    quantifier_probe_hits: int = 0
    class_labels: Mapping[str, str] = field(default_factory=dict)

    @property
    def datasheets(self) -> int:
        return sum(f.datasheets for f in self.factions)

    @property
    def rows(self) -> int:
        return sum(f.rows for f in self.factions)

    @property
    def unparsed(self) -> int:
        return sum(f.unparsed for f in self.factions)

    @property
    def partial_datasheets(self) -> int:
        return sum(f.partial_datasheets for f in self.factions)

    @property
    def ratio(self) -> float:
        return self.unparsed / self.rows if self.rows else 0.0

    def share(self, *keys: str) -> float:
        """The share of the residual a set of classes accounts for."""
        covered = sum(self.classes.get(key, 0) for key in keys)
        return covered / self.unparsed if self.unparsed else 0.0


#: The four productions 006 tasks T016-T017 build, in build order, and what each is expected to
#: clear. **This is what T002 confirms or contradicts** — the build order is sized against this
#: run's own numbers, never against research D1's ≈81 %-sample figures.
BUILD_ORDER: Final[tuple[tuple[str, str], ...]] = (
    ("T016", "1a"),
    ("T016", "1b"),
    ("T016", "1f"),
    ("T017", "1c"),
    ("T017", "1e"),
    ("T017", "1d"),
)


def measure(
    config: PipelineConfig,
    *,
    repository_root: Path,
    fixtures_dir: Path | None = None,
    offline: bool = False,
    generated_at: datetime | None = None,
) -> TaxonomyReport:
    """Acquire, classify, discard — and return only the counts.

    Every acquired string lives inside the ``with workspace(...)`` block and is classified there;
    what comes back out is integers. That is not a stylistic choice. It is the shape that makes
    "no source text exists anywhere else" true rather than asserted.
    """
    class_counts: dict[str, int] = {rule.key: 0 for rule in _CLASSES}
    feature_counts: dict[str, int] = {key: 0 for key, _label in _FEATURES}
    conflated = 0
    dropped_quantifiers = 0
    unparsed_quantifiers = 0
    probe_hits = 0
    per_faction: list[FactionTaxonomy] = []

    with workspace(repository_root) as work:
        acquisition, payloads = acquire_detail(
            config, fixtures_dir=fixtures_dir, offline=offline, workspace=work
        )
        source = acquisition.source_base_url
        tables = read_detail(config, payloads)
        faction_of = {
            row.fields["id"]: row.fields.get("faction_id", "")
            for row in tables[_DATASHEETS_TABLE].rows
        }
        datasheets_per_faction: dict[str, int] = {}
        for faction_id in faction_of.values():
            datasheets_per_faction[faction_id] = datasheets_per_faction.get(faction_id, 0) + 1

        rows_per_faction: dict[str, int] = {}
        unparsed_per_faction: dict[str, int] = {}
        option_datasheets: dict[str, set[str]] = {}
        partial_datasheets: dict[str, set[str]] = {}

        for row in tables[_OPTIONS_TABLE].rows:
            datasheet_id = row.fields.get("datasheet_id", "")
            faction_id = faction_of.get(datasheet_id, "")
            description = row.fields.get("description", "")
            rows_per_faction[faction_id] = rows_per_faction.get(faction_id, 0) + 1
            option_datasheets.setdefault(faction_id, set()).add(datasheet_id)

            stem_raw, items = split_sublist(description)
            stem = pre_pass(stem_raw, field="option.description")
            if (
                _QUANTIFIER_PROBE.search(stem) is not None
                and _BOILERPLATE_FOLLOWING.search(stem) is None
            ):
                probe_hits += 1
            parsed = parse_row(description)
            if parsed is None:
                unparsed_per_faction[faction_id] = unparsed_per_faction.get(faction_id, 0) + 1
                partial_datasheets.setdefault(faction_id, set()).add(datasheet_id)
                class_counts[classify(stem)] += 1
                for feature in features_of(stem, items):
                    feature_counts[feature] += 1
                if _SELECT_QUANTIFIER.search(stem) is not None:
                    # Counted on the residual as well as on the parsing rows, because which
                    # side of the line these sit on decides what T019 actually is: a fix to
                    # rows that publish "pick any number" today, or a field a NEW production
                    # has to populate as it resolves the row for the first time.
                    unparsed_quantifiers += 1
                continue

            # The row parsed. D1d's two silent-failure classes live here, and they are the
            # reason this loop looks at successes at all: a row that resolves *differently* from
            # what the source says is invisible to any coverage figure, because it resolved.
            if any(_CONFLATED_NAME.search(choice.name) is not None for choice in parsed.choices):
                conflated += 1
            _stem_head, remainder = _split_on_verb(stem)
            if items and _SELECT_QUANTIFIER.search(remainder) is not None:
                dropped_quantifiers += 1

    for faction_id in sorted(datasheets_per_faction | rows_per_faction):
        per_faction.append(
            FactionTaxonomy(
                faction_id=faction_id or "(unattributed)",
                datasheets=datasheets_per_faction.get(faction_id, 0),
                datasheets_with_options=len(option_datasheets.get(faction_id, ())),
                rows=rows_per_faction.get(faction_id, 0),
                unparsed=unparsed_per_faction.get(faction_id, 0),
                partial_datasheets=len(partial_datasheets.get(faction_id, ())),
            )
        )

    moment = (generated_at or datetime.now(UTC)).astimezone(UTC)
    return TaxonomyReport(
        generated_at=moment.isoformat().replace("+00:00", "Z"),
        mode=config.detail_acquisition_mode.value,
        edition=config.detail_edition,
        source=source,
        factions=tuple(per_faction),
        classes=dict(class_counts),
        features=dict(feature_counts),
        parsed_conflated_names=conflated,
        parsed_dropped_quantifiers=dropped_quantifiers,
        unparsed_select_quantifiers=unparsed_quantifiers,
        quantifier_probe_hits=probe_hits,
        class_labels={rule.key: rule.label for rule in _CLASSES},
    )


# =================================================================================================
# 009 task T001 -- the export-mode comparison. FR-004 requires the taxonomy re-run in `csv` mode
# over the SAME current-edition corpus as the existing `html`-mode measurement, with per-
# diagnosis-class residuals placed side by side rather than reduced to two aggregate percentages,
# plus a row-granularity section for research.md Q1. Both arms are measured inside one process so
# "the same corpus" is a fact about when the two acquisitions ran, not an assumption.
# =================================================================================================


@dataclass(frozen=True, slots=True)
class ModeResidual:
    """One acquisition mode's option residual, classified by `classify()` -- the unit the
    comparison places side by side. Rows are keyed by the datasheet's case-folded NAME, not its
    id: `html` mode's id joins the faction slug to the page anchor, and `csv` mode's is the
    export's own numeric id, so name is the only join key the two arms share (the same collapse
    `_card_shapes` uses elsewhere in this file)."""

    mode: str
    datasheets: int
    rows: int
    unparsed: int
    classes: Mapping[str, int]
    rows_per_datasheet: Mapping[str, int]
    unparsed_per_datasheet: Mapping[str, int]

    @property
    def ratio(self) -> float:
        return self.unparsed / self.rows if self.rows else 0.0


@dataclass(frozen=True, slots=True)
class RowGranularity:
    """research.md Q1: does the export split a card's option list into the same rows the html arm
    does. Counts and a histogram only -- no row text, in either direction."""

    shared_names: int
    equal_count: int
    differing_count: int
    csv_only_names: int
    html_only_names: int
    csv_unparsed_rows_on_differing: int
    html_unparsed_rows_on_differing: int
    csv_histogram: Mapping[int, int]
    html_histogram: Mapping[int, int]


@dataclass(frozen=True, slots=True)
class ModeComparisonReport:
    """T001's whole deliverable: two `ModeResidual`s over the same corpus, plus the granularity
    section. Text-free -- counts, class keys, and datasheet NAMES never appear; only their
    case-folded identity is used, internally, as a join key."""

    generated_at: str
    edition: str
    source: str
    csv: ModeResidual
    html: ModeResidual
    granularity: RowGranularity
    class_labels: Mapping[str, str] = field(default_factory=dict)


def _measure_mode_residual(
    config: PipelineConfig,
    mode: DetailAcquisitionMode,
    *,
    repository_root: Path,
    fixtures_dir: Path | None,
    offline: bool,
) -> ModeResidual:
    """One arm's residual, over whatever `config` (with `mode` substituted) resolves to acquire.

    Mirrors `measure()`'s acquire-classify-discard shape; kept separate because `measure()`'s
    per-faction breakdown is a different axis than the per-datasheet-name one this comparison
    needs to join the two arms on.
    """
    mode_config = replace(config, detail_acquisition_mode=mode)
    class_counts: dict[str, int] = {rule.key: 0 for rule in _CLASSES}
    rows_per_name: dict[str, int] = {}
    unparsed_per_name: dict[str, int] = {}
    names_seen: set[str] = set()
    rows_total = 0
    unparsed_total = 0

    with workspace(repository_root) as work:
        _acquisition, payloads = acquire_detail(
            mode_config, fixtures_dir=fixtures_dir, offline=offline, workspace=work
        )
        tables = read_detail(mode_config, payloads)
        name_of = {
            row.fields.get("id", ""): row.fields.get("name", "").strip().casefold()
            for row in tables[_DATASHEETS_TABLE].rows
        }
        for row in tables[_OPTIONS_TABLE].rows:
            datasheet_id = row.fields.get("datasheet_id", "")
            name = name_of.get(datasheet_id, "")
            names_seen.add(name)
            description = row.fields.get("description", "")
            rows_total += 1
            rows_per_name[name] = rows_per_name.get(name, 0) + 1

            stem_raw, _items = split_sublist(description)
            stem = pre_pass(stem_raw, field="option.description")
            parsed = parse_row(description)
            if parsed is None:
                unparsed_total += 1
                unparsed_per_name[name] = unparsed_per_name.get(name, 0) + 1
                class_counts[classify(stem)] += 1

    return ModeResidual(
        mode=mode.value,
        datasheets=len(names_seen),
        rows=rows_total,
        unparsed=unparsed_total,
        classes=dict(class_counts),
        rows_per_datasheet=dict(rows_per_name),
        unparsed_per_datasheet=dict(unparsed_per_name),
    )


def _histogram(counts: Mapping[str, int]) -> dict[int, int]:
    histogram: dict[int, int] = {}
    for count in counts.values():
        histogram[count] = histogram.get(count, 0) + 1
    return dict(sorted(histogram.items()))


def _row_granularity(csv_residual: ModeResidual, html_residual: ModeResidual) -> RowGranularity:
    """Compare option-row counts per datasheet NAME between the two arms.

    A name present in both arms with a differing row count is exactly the shape research.md Q1
    asks about: the stem-versus-alternative geometry the grammar reads may have changed underneath
    it. Reported as counts and a distribution only.
    """
    csv_names = set(csv_residual.rows_per_datasheet)
    html_names = set(html_residual.rows_per_datasheet)
    shared = csv_names & html_names
    differing = {
        name
        for name in shared
        if csv_residual.rows_per_datasheet[name] != html_residual.rows_per_datasheet[name]
    }
    equal = shared - differing

    csv_unparsed_on_differing = sum(
        csv_residual.unparsed_per_datasheet.get(name, 0) for name in differing
    )
    html_unparsed_on_differing = sum(
        html_residual.unparsed_per_datasheet.get(name, 0) for name in differing
    )

    return RowGranularity(
        shared_names=len(shared),
        equal_count=len(equal),
        differing_count=len(differing),
        csv_only_names=len(csv_names - html_names),
        html_only_names=len(html_names - csv_names),
        csv_unparsed_rows_on_differing=csv_unparsed_on_differing,
        html_unparsed_rows_on_differing=html_unparsed_on_differing,
        csv_histogram=_histogram(csv_residual.rows_per_datasheet),
        html_histogram=_histogram(html_residual.rows_per_datasheet),
    )


def measure_mode_comparison(
    config: PipelineConfig,
    *,
    repository_root: Path,
    fixtures_dir: Path | None = None,
    offline: bool = False,
    generated_at: datetime | None = None,
) -> ModeComparisonReport:
    """FR-004's rig: both arms, over the same current-edition corpus, in one process.

    `config.detail_acquisition_mode` is not read here beyond determining `edition`/`source` for
    the report header -- each arm substitutes its own mode via `dataclasses.replace`, so a single
    invocation (regardless of which mode `WGC_DETAIL_ACQUISITION_MODE` currently names) measures
    both.
    """
    csv_residual = _measure_mode_residual(
        config,
        DetailAcquisitionMode.CSV,
        repository_root=repository_root,
        fixtures_dir=fixtures_dir,
        offline=offline,
    )
    html_residual = _measure_mode_residual(
        config,
        DetailAcquisitionMode.HTML,
        repository_root=repository_root,
        fixtures_dir=fixtures_dir,
        offline=offline,
    )
    granularity = _row_granularity(csv_residual, html_residual)
    moment = (generated_at or datetime.now(UTC)).astimezone(UTC)
    return ModeComparisonReport(
        generated_at=moment.isoformat().replace("+00:00", "Z"),
        edition=config.detail_edition,
        source=config.detail_source_url,
        csv=csv_residual,
        html=html_residual,
        granularity=granularity,
        class_labels={rule.key: rule.label for rule in _CLASSES},
    )


def render_mode_comparison(report: ModeComparisonReport) -> str:
    """T001's report as Markdown. Counts, class labels, and a row-count histogram only -- no
    source sentence, no fragment, no item name, no datasheet name."""
    lines = [
        "<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Generated by "
        "tools/option_taxonomy.py --compare-modes (009 T001). -->",
        "# Export-mode option-residual comparison",
        "",
        f"- Generated: `{report.generated_at}`",
        f"- Declared detail edition: `{report.edition}`",
        f"- Source: `{report.source}`",
        "",
        "**Non-destructive, and text-free.** Both arms were acquired into an ephemeral workspace "
        "discarded at run end. Nothing under `data/`, `curation/`, or `state/` was written, and no "
        "source sentence, fragment, item name, or datasheet name appears on this page -- rows are "
        "joined between arms on a case-folded name internally and only the join's own counts are "
        "reported.",
        "",
        "## Aggregate, both arms over the same corpus",
        "",
        "| Mode | Datasheets | Option rows | Unparsed | Share unparsed |",
        "|---|---:|---:|---:|---:|",
        f"| `{report.csv.mode}` | {report.csv.datasheets} | {report.csv.rows} | "
        f"{report.csv.unparsed} | {report.csv.ratio:.1%} |",
        f"| `{report.html.mode}` | {report.html.datasheets} | {report.html.rows} | "
        f"{report.html.unparsed} | {report.html.ratio:.1%} |",
        "",
        "## The residual, by class, side by side (FR-004, FR-005)",
        "",
        "Disjoint and ordered per arm -- each arm's own column sums to that arm's own residual "
        "above.",
        "",
        "| Class | Shape | `csv` rows | `html` rows | Delta (csv - html) |",
        "|---|---|---:|---:|---:|",
    ]
    for key in sorted(report.class_labels, key=_class_sort_key):
        label = report.class_labels[key]
        csv_count = report.csv.classes.get(key, 0)
        html_count = report.html.classes.get(key, 0)
        delta = csv_count - html_count
        lines.append(f"| **{key}** | {label} | {csv_count} | {html_count} | {delta} |")

    g = report.granularity
    lines += [
        "",
        "## Row granularity (research.md Q1)",
        "",
        "Option-row counts per datasheet, joined between arms by case-folded name -- the only key "
        "the two arms share (`html`'s id joins the faction slug to the page anchor; `csv`'s is the "
        "export's own numeric id).",
        "",
        "| Shared names | Same row count in both arms | Differing row count | `csv`-only names | "
        "`html`-only names |",
        "|---:|---:|---:|---:|---:|",
        f"| {g.shared_names} | {g.equal_count} | {g.differing_count} | {g.csv_only_names} | "
        f"{g.html_only_names} |",
        "",
        f"Of the residual above, **{g.csv_unparsed_rows_on_differing}** `csv`-mode unparsed rows "
        f"and **{g.html_unparsed_rows_on_differing}** `html`-mode unparsed rows sit on a datasheet "
        "whose row count differs between arms -- the population a granularity cause (rather than a "
        "normalization or vocabulary one) could explain.",
        "",
        "Rows-per-datasheet distribution (row count -> datasheets):",
        "",
        "| Rows | `csv` datasheets | `html` datasheets |",
        "|---:|---:|---:|",
    ]
    all_counts = sorted(set(g.csv_histogram) | set(g.html_histogram))
    for count in all_counts:
        csv_n = g.csv_histogram.get(count, 0)
        html_n = g.html_histogram.get(count, 0)
        lines.append(f"| {count} | {csv_n} | {html_n} |")

    lines += [
        "",
        "## Reading this",
        "",
        "- **This is the rig FR-004's diagnosis rests on.** It attributes nothing by itself -- "
        "`reports/009-diagnosis/`'s cause-attribution work reads this table's deltas and assigns "
        "each to a denominator, normalization, or vocabulary cause.",
        "- A name absent from one arm (`csv`-only or `html`-only) is not a parsing difference; it "
        "is an enumeration difference between the two acquisitions and is reported separately, "
        "never folded into a class delta.",
        "",
    ]
    return "\n".join(lines)


def _percent(part: int, whole: int) -> str:
    return f"{part / whole:.1%}" if whole else "—"


def render(report: TaxonomyReport) -> str:
    """The measurement as Markdown.

    Counts only — never a sentence, never a fragment, never an item name.
    """
    lines = [
        "<!-- AI-Assisted: Claude Code (model: claude-opus-5) - Generated by "
        "tools/option_taxonomy.py (006 T001/T002). -->",
        "# Option-row taxonomy",
        "",
        f"- Generated: `{report.generated_at}`",
        f"- Detail acquisition mode: `{report.mode}`",
        f"- Declared detail edition: `{report.edition}`",
        f"- Source: `{report.source}`",
        "",
        "**Non-destructive, and text-free.** Nothing under `data/`, `curation/`, or `state/` was "
        "written, the acquired pages were discarded with `work/` when the run ended, and no "
        "source sentence, fragment, or item name appears on this page. It carries counts.",
        "",
        "## Corpus",
        "",
        "| Datasheets | Option rows | `OPT-UNPARSED` | Share unparsed | Datasheets with an "
        "unparsed row |",
        "|---:|---:|---:|---:|---:|",
        f"| {report.datasheets} | {report.rows} | **{report.unparsed}** | {report.ratio:.1%} | "
        f"{report.partial_datasheets} |",
        "",
        "## The residual, by class (research D1b)",
        "",
        "Disjoint and ordered — each row lands in exactly one class, so these counts sum to the "
        "residual above.",
        "",
        "| Class | Shape | Rows | Share of residual |",
        "|---|---|---:|---:|",
    ]
    for key in sorted(report.classes, key=_class_sort_key):
        count = report.classes[key]
        label = report.class_labels.get(key, key)
        lines.append(f"| **{key}** | {label} | {count} | {_percent(count, report.unparsed)} |")

    lines += [
        "",
        "## Cross-cutting features (same rows, overlapping)",
        "",
        "These do **not** sum to the residual and are not meant to: one sentence routinely "
        "carries three of them. Each names a capability the grammar must carry rather than a "
        "production it must add.",
        "",
        "| Feature | Rows | Share of residual |",
        "|---|---:|---:|",
    ]
    for key, label in _FEATURES:
        count = report.features.get(key, 0)
        lines.append(f"| {label} | {count} | {_percent(count, report.unparsed)} |")

    lines += [
        "",
        "## The build order this run sizes (006 T016-T017)",
        "",
        "| After | Classes cleared | Cumulative rows | Cumulative share of residual |",
        "|---|---|---:|---:|",
    ]
    seen: list[str] = []
    for task, key in BUILD_ORDER:
        seen.append(key)
        covered = sum(report.classes.get(k, 0) for k in seen)
        lines.append(
            f"| {task} | {', '.join(seen)} | {covered} | {_percent(covered, report.unparsed)} |"
        )

    lines += [
        "",
        "## The silent-failure classes, over the rows that DO parse (research D1d)",
        "",
        "Neither of these is in the residual above: both rows parsed. They are counted because a "
        "row that resolves *differently* from what the source says is invisible to any coverage "
        "figure — it resolved.",
        "",
        "| Class | Rows | Bears on |",
        "|---|---:|---|",
        f"| A choice `name` that conflates a multi-item bundle | {report.parsed_conflated_names} "
        "| 006 T018 decomposes these into items **without renaming them** (the O1 Ruling) |",
        f"| A group-level select quantifier dropped from the stem | "
        f"{report.parsed_dropped_quantifiers} | 006 T019 populates the already-declared "
        "`minChoices`/`maxChoices` |",
        f"| *(for contrast)* a select quantifier in a row that does **not** parse | "
        f"{report.unparsed_select_quantifiers} | the same quantifier, on the other side of the "
        "line: T019 populates it as a new production resolves the row, not as a fix to a row "
        "that already publishes |",
        f"| *(loose probe)* any stem stating `… of the following` other than the `one of the "
        f"following` boilerplate | {report.quantifier_probe_hits} | a zero on the two rows "
        "above is only meaningful if this one is small too — otherwise the strict pattern "
        "missed the corpus's own phrasing |",
        "",
        "## Per faction",
        "",
        "| Faction | Datasheets | With options | Option rows | Unparsed | Share | Datasheets with "
        "an unparsed row |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for faction in sorted(report.factions, key=lambda f: (-f.unparsed, f.faction_id)):
        lines.append(
            f"| `{faction.faction_id}` | {faction.datasheets} | "
            f"{faction.datasheets_with_options} | {faction.rows} | {faction.unparsed} | "
            f"{faction.ratio:.1%} | {faction.partial_datasheets} |"
        )

    lines += [
        "",
        "## Reading this",
        "",
        "- **The build order table is the point.** 006 tasks T016-T017 are sized against this "
        "run's own numbers, never against research D1's ≈81 %-sample projection. A class rarer "
        "here than D1 measured costs an unused production, not a defect; a class *larger* here "
        "moves it up the order.",
        "- Classes **6** and **11** are extractor bugs, not grammar gaps (research D1c.4). They "
        "are fixed in `parse/wahapedia_html_dom.py::_options` (006 T022) and never reach the "
        "grammar, so they are excluded from what any production is expected to clear.",
        "- Class **9** is a group *availability predicate*, not clause vocabulary. No production "
        "is planned for it; it stays `OPT-UNPARSED` and is curator-override material.",
        "- Nothing here is a defect list. The residual tail is budgeted editorial and "
        "engineering work and is expected to shrink, not vanish.",
        "",
    ]
    return "\n".join(lines)


def _class_sort_key(key: str) -> tuple[int, str]:
    """Numeric class order with the ``1a``-``1f`` sub-classes kept under class 1."""
    digits = "".join(ch for ch in key if ch.isdigit())
    return int(digits or 0), key


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Classify the unparsed wargear-option rows of a corpus, retaining nothing.",
    )
    parser.add_argument("--fixtures", type=Path, help="source from a synthetic fixture set")
    parser.add_argument(
        "--offline", action="store_true", help="refuse network access; requires --fixtures"
    )
    parser.add_argument(
        "--out", type=Path, help="report path (default reports/option-taxonomy/<date>.md)"
    )
    parser.add_argument("--repo", type=Path, help="repository root (default: this checkout)")
    parser.add_argument(
        "--print-only", action="store_true", help="render to stdout and write no file"
    )
    parser.add_argument(
        "--compare-modes",
        action="store_true",
        help=(
            "009 T001: measure BOTH csv and html mode over the same current-edition corpus and "
            "render the per-diagnosis-class comparison (default report path "
            "reports/009-diagnosis/<date>.md) instead of the single-mode report"
        ),
    )
    return parser.parse_args(list(argv) if argv is not None else None)


#: 009 T001's own report directory -- distinct from `REPORTS_DIR` so this comparison is never
#: mistaken for the single-mode taxonomy report it sits beside.
DIAGNOSIS_REPORTS_DIR: Final = Path("reports") / "009-diagnosis"


def _summary_line(report: TaxonomyReport) -> str:
    top = sorted(report.classes.items(), key=lambda item: (-item[1], item[0]))[:1]
    leader = f"{top[0][0]} ({top[0][1]})" if top and top[0][1] else "none"
    return (
        f"{PROG}: {report.unparsed} of {report.rows} option rows unparsed "
        f"({report.ratio:.1%}) over {report.datasheets} datasheets; largest class {leader}"
    )


def _main_compare_modes(args: argparse.Namespace, root: Path) -> int:
    """009 T001: measure both arms and render the comparison. Separated from `main` because the
    single-mode path's `load_config`/`measure` error handling names one mode; this path always
    exercises both regardless of which mode `WGC_DETAIL_ACQUISITION_MODE` currently names."""
    try:
        config = load_config()
        report = measure_mode_comparison(
            config, repository_root=root, fixtures_dir=args.fixtures, offline=args.offline
        )
    except ConfigError as exc:
        print(f"{PROG}: {exc}", file=sys.stderr)
        return int(ExitCode.CONFIG_ERROR)
    except AcquisitionError as exc:
        print(f"{PROG}: {exc}", file=sys.stderr)
        return int(exc.exit_code)

    rendered = render_mode_comparison(report)
    if args.print_only:
        print(rendered)
    else:
        destination = args.out or (root / DIAGNOSIS_REPORTS_DIR / f"{report.generated_at[:10]}.md")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"{PROG}: wrote {destination}")

    print(
        f"{PROG}: csv {report.csv.unparsed}/{report.csv.rows} ({report.csv.ratio:.1%}) vs "
        f"html {report.html.unparsed}/{report.html.rows} ({report.html.ratio:.1%}) unparsed"
    )
    return int(ExitCode.SUCCESS)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    root = args.repo or repo_root()

    if args.compare_modes:
        return _main_compare_modes(args, root)

    try:
        config = load_config()
        report = measure(
            config, repository_root=root, fixtures_dir=args.fixtures, offline=args.offline
        )
    except ConfigError as exc:
        # Named without its value, here as everywhere. A live invocation with
        # WGC_DETAIL_SOURCE_URL unset is this tool's most likely failure and has to stop as the
        # configuration error it is, not as a partial upstream export.
        print(f"{PROG}: {exc}", file=sys.stderr)
        return int(ExitCode.CONFIG_ERROR)
    except AcquisitionError as exc:
        print(f"{PROG}: {exc}", file=sys.stderr)
        return int(exc.exit_code)

    rendered = render(report)
    evidence = load_published_snapshot_evidence(root, edition_code=config.detail_edition)
    if evidence is not None:
        excluded = excluded_populations(evidence.snapshot, evidence.findings)
        zero_group = zero_group_breakdown(evidence.snapshot)
        census = conditional_blocking_census(
            evidence.findings,
            measured_conditional_rows=SC002_MEASURED_CONDITIONAL_ROWS,
            measured_total_unparsed_rows=SC002_MEASURED_TOTAL_UNPARSED_ROWS,
            sc002_headroom=SC002_HEADROOM,
        )
        rendered += render_snapshot_sections(
            evidence, excluded=excluded, zero_group=zero_group, census=census
        )
        worklist = override_candidate_worklist(evidence.findings)
        rendered += render_override_candidate_worklist(
            worklist, rules_version_id=evidence.rules_version_id
        )

    if args.print_only:
        print(rendered)
    else:
        destination = args.out or (root / REPORTS_DIR / f"{report.generated_at[:10]}.md")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"{PROG}: wrote {destination}")

    print(_summary_line(report))
    return int(ExitCode.SUCCESS)


#: The diagnosis-class-level figures from the last **live** run of
#: `reports/footnote-restriction-taxonomy/2026-08-14.md` (`tools/item_constraint_taxonomy.py`,
#: which calls the options grammar's own private refusal/head/verb/object functions directly on
#: the live corpus) — 2422 rows, 206 unparsed: `head_ok_no_verb` 139, `refused_conditional_or_
#: equipment_qualified` 50, `no_head_match` 17. Carried forward rather than re-measured, and named
#: as constants rather than inlined, because T003's census and T014's O2 sizing both read them.
SC002_MEASURED_CONDITIONAL_ROWS: Final = 50
SC002_MEASURED_TOTAL_UNPARSED_ROWS: Final = 206

#: SC-002 needs a gain of 126 datasheets (92% -> 98% of 2084) from a partial population of 162, of
#: which 15 are excluded as the item-constraint vocabulary gap (spec Edge Cases), leaving 147
#: addressable — so up to 147-126=21 of those 147 may fail to close and SC-002 still holds.
SC002_HEADROOM: Final = 21


def iter_class_keys() -> Iterable[str]:
    """Every taxonomy class key, in report order — a convenience for tests and reports."""
    return sorted((rule.key for rule in _CLASSES), key=_class_sort_key)


# =================================================================================================
# 008 task T001(b)/(c), T003, T004 — the zero-group breakdown, the card-shape collapse, and the
# conditional-blocking census.
#
# **Why this section reads a different source than everything above.** `classify()` and
# `measure()` answer "why did the grammar refuse this row", which only the raw acquired sentence
# can answer. The three questions this section answers — "does this datasheet publish ANY option
# group", "how many DISTINCT card shapes does a population of datasheets collapse to", and "how
# many datasheets can no production or override ever fully close" — are questions about what the
# pipeline already **published**, not about a sentence's grammar. They are answered from the
# pipeline's own curated tree (`data/<edition-code>/`, read the same way
# `pipeline.validate.gates.check_option_ratchet`'s prior-snapshot comparison already does) and the
# retained validation report of the previous published version (`reports/<rulesVersionId>/
# report.json`) — both git-tracked, both already governed by the pipeline's own acquisition and
# curation, and neither requiring a source fetch of any kind. This is committed/published evidence
# on the same terms `tools/consumer_compat.py::run` already reads a released bundle by path.
# =================================================================================================


def _card_shapes(names: Iterable[str]) -> int:
    """Case-insensitive name collapse — spec's *Card Shape*: one shape, several factions' clones.

    Confirmed against the spec's own committed census (42/28, 120/80, 47/24): collapsing a
    population's datasheet names this way reproduces every one of those six numbers exactly,
    which is the strongest evidence available in this repository that this is the method the
    census itself used.
    """
    return len({name.strip().casefold() for name in names})


@dataclass(frozen=True, slots=True)
class ZeroGroupBreakdown:
    """T001(b): does a `partial` datasheet publish not one option group, or merely not all of
    them. The two populations US1 and US2 are sized against (spec's Key Entities: *Zero-Group
    Partial Datasheet*)."""

    zero_group_datasheets: int
    zero_group_shapes: int
    some_group_datasheets: int
    some_group_shapes: int
    zero_group_ids: tuple[str, ...]
    some_group_ids: tuple[str, ...]


def zero_group_breakdown(snapshot: CuratedSnapshot) -> ZeroGroupBreakdown:
    """Split every `wargear_option_state = partial` datasheet by whether it publishes a group."""
    is_partial = WargearOptionState.PARTIAL
    partial = [d for d in snapshot.datasheets if d.wargear_option_state == is_partial]
    zero = sorted((d for d in partial if not d.option_groups), key=lambda d: d.datasheet_id)
    some = sorted((d for d in partial if d.option_groups), key=lambda d: d.datasheet_id)
    return ZeroGroupBreakdown(
        zero_group_datasheets=len(zero),
        zero_group_shapes=_card_shapes(d.name for d in zero),
        some_group_datasheets=len(some),
        some_group_shapes=_card_shapes(d.name for d in some),
        zero_group_ids=tuple(d.datasheet_id for d in zero),
        some_group_ids=tuple(d.datasheet_id for d in some),
    )


@dataclass(frozen=True, slots=True)
class ExcludedPopulations:
    """T004: the two populations the spec excludes from every target, so they are never counted
    as unresolved work — by datasheet id, so the exclusion is checkable rather than asserted."""

    item_constraint_vocabulary_gap: tuple[str, ...]
    """`partial` only because a restriction-shaped row fell out of `007`'s two-member
    item-constraint vocabulary (`docs/follow-ups.md` item 15) — carries `CST-UNPARSED` and no
    `OPT-UNPARSED` finding at all. Spec: 15."""

    no_option_state_at_all: tuple[str, ...]
    """`wargear_option_state` is OMITTED (not `none`, not `partial`) — the source was never
    consulted for this datasheet, data-model.md §3's fourth state. Spec: the four Chaos Titans,
    Myphitic Blight-haulers, Vyper — 6."""


def excluded_populations(
    snapshot: CuratedSnapshot, findings: Sequence[Mapping[str, object]]
) -> ExcludedPopulations:
    """Compute both exclusion sets from the curated tree and the retained candidate report's own
    findings (`OPT-UNPARSED`, text-free: datasheet id, file name, row ordinal only)."""
    opt_unparsed_ids: set[str] = set()
    for finding in findings:
        if finding.get("finding_code") != "OPT-UNPARSED":
            continue
        detail = finding.get("detail")
        if isinstance(detail, Mapping):
            datasheet_id = detail.get("datasheet_id")
            if isinstance(datasheet_id, str):
                opt_unparsed_ids.add(datasheet_id)

    partial_ids = {
        d.datasheet_id
        for d in snapshot.datasheets
        if d.wargear_option_state == WargearOptionState.PARTIAL
    }
    vocabulary_gap = tuple(sorted(partial_ids - opt_unparsed_ids))
    no_state = tuple(
        sorted(d.datasheet_id for d in snapshot.datasheets if d.wargear_option_state is None)
    )
    return ExcludedPopulations(vocabulary_gap, no_state)


@dataclass(frozen=True, slots=True)
class ConditionalBlockingCensus:
    """T003: sizes Open Decision O2 — is SC-002's 98% reachable at all.

    `estimate_low`/`estimate_high` are an **estimate bounded by measurement, not a measurement**:
    the retained candidate report names which datasheet each `OPT-UNPARSED` row belongs to, but
    not which taxonomy diagnosis class that row is (that classification requires the raw sentence,
    which this environment has no route to acquire — see the report's own methodology note). The
    range is honestly reported as a range for exactly that reason.
    """

    unparsed_row_datasheets: int
    unparsed_rows_total: int
    single_row_datasheets: int
    row_count_histogram: Mapping[int, int]
    measured_conditional_rows: int
    measured_total_unparsed_rows: int
    estimate_low: int
    estimate_high: int
    sc002_headroom: int


def conditional_blocking_census(
    findings: Sequence[Mapping[str, object]],
    *,
    measured_conditional_rows: int,
    measured_total_unparsed_rows: int,
    sc002_headroom: int,
) -> ConditionalBlockingCensus:
    """Build the per-datasheet `OPT-UNPARSED` row-count histogram and bound the conditional-only
    count from it.

    ``estimate_low``: the measured conditional share applied to the single-row population only —
    the assumption that a conditional stem is usually the datasheet's *only* unparsed row (the
    diagnosis table's own signal columns support this: a `refused_conditional_or_equipment_
    qualified` row is a whole-clause predicate, not a fragment sharing a row with other clause
    vocabulary). ``estimate_high``: the theoretical concentration bound — every measured
    conditional row landing on its own, otherwise-single-row datasheet, capped at the single-row
    population itself. Both are stated; neither is asserted as exact.
    """
    per_datasheet: dict[str, int] = {}
    for finding in findings:
        if finding.get("finding_code") != "OPT-UNPARSED":
            continue
        detail = finding.get("detail")
        if not isinstance(detail, Mapping):
            continue
        datasheet_id = detail.get("datasheet_id")
        if isinstance(datasheet_id, str):
            per_datasheet[datasheet_id] = per_datasheet.get(datasheet_id, 0) + 1

    histogram: dict[int, int] = {}
    for count in per_datasheet.values():
        histogram[count] = histogram.get(count, 0) + 1
    single_row = histogram.get(1, 0)

    share = (
        measured_conditional_rows / measured_total_unparsed_rows
        if measured_total_unparsed_rows
        else 0.0
    )
    estimate_low = round(single_row * share)
    estimate_high = min(measured_conditional_rows, single_row)

    return ConditionalBlockingCensus(
        unparsed_row_datasheets=len(per_datasheet),
        unparsed_rows_total=sum(per_datasheet.values()),
        single_row_datasheets=single_row,
        row_count_histogram=dict(sorted(histogram.items())),
        measured_conditional_rows=measured_conditional_rows,
        measured_total_unparsed_rows=measured_total_unparsed_rows,
        estimate_low=min(estimate_low, estimate_high),
        estimate_high=estimate_high,
        sc002_headroom=sc002_headroom,
    )


# -- 008 Phase 7 (T071/T072 preparation) ---------------------------------------------------------
# The worklist a curator needs before writing `curation/option-overrides.json`'s real entries:
# which datasheet, which line. `ConditionalBlockingCensus` above already builds a per-datasheet
# row COUNT for O2's own purpose; this keeps the row NUMBERS themselves, because an override is
# keyed `(datasheet_id, line)` and a curator opening the source card needs the line to find the
# row, not merely how many rows the datasheet has.


@dataclass(frozen=True, slots=True)
class OverrideCandidateWorklist:
    """Every `OPT-UNPARSED` row the retained report names, grouped by datasheet.

    **This is a worklist, not a candidate report's worth of overrides.** It says WHERE to look,
    never what to write there — no item name, no scope, no choice ever appears here, because none
    of those is derivable from `report.json`'s text-free finding detail (`datasheet_id`, `line`
    only). Authoring the row itself is T071's own job, done by a human reading the source card.

    **It is also stale by construction**, and deliberately not disguised as anything else: this
    feature's own Phase 3/4 productions (`_COMPLETION_VERBS`) did not exist when the retained
    `report.json` this reads was generated, so a row named here may already resolve once those
    productions run against a current corpus. T074's mid-campaign dry-run — run AFTER every
    Phase 3-6 production is in place, BEFORE a single override is authored — is what turns this
    into the real, current worklist (tasks.md's own explicit ordering: "only the real-corpus
    dry-run can say which rows those are"). This function exists so that dry-run has a
    ready-made, tested shape to populate rather than inventing one under time pressure.
    """

    rows_by_datasheet: Mapping[str, tuple[int, ...]]
    total_rows: int
    total_datasheets: int


def override_candidate_worklist(
    findings: Sequence[Mapping[str, object]],
) -> OverrideCandidateWorklist:
    per_datasheet: dict[str, list[int]] = {}
    for finding in findings:
        if finding.get("finding_code") != "OPT-UNPARSED":
            continue
        detail = finding.get("detail")
        if not isinstance(detail, Mapping):
            continue
        datasheet_id = detail.get("datasheet_id")
        line = detail.get("line")
        if isinstance(datasheet_id, str) and isinstance(line, int):
            per_datasheet.setdefault(datasheet_id, []).append(line)

    rows_by_datasheet = {
        datasheet_id: tuple(sorted(lines)) for datasheet_id, lines in sorted(per_datasheet.items())
    }
    return OverrideCandidateWorklist(
        rows_by_datasheet=rows_by_datasheet,
        total_rows=sum(len(lines) for lines in rows_by_datasheet.values()),
        total_datasheets=len(rows_by_datasheet),
    )


def render_override_candidate_worklist(
    worklist: OverrideCandidateWorklist, *, rules_version_id: str
) -> str:
    """T071/T072 preparation, as its own Markdown section — counts and `datasheet_id#line` pairs
    only, never a sentence, a fragment, or an item name."""
    lines = [
        "",
        "## Override-candidate worklist (T071/T072 preparation)",
        "",
        f"Read from `reports/{rules_version_id}/report.json`'s own `OPT-UNPARSED` findings — "
        "text-free (`datasheet_id`, `line` only). **Stale by construction** (see "
        "`OverrideCandidateWorklist`'s own docstring): this predates Phase 3-6's productions, so "
        "it names WHERE the pre-008 residual was, not the current one. **Not a substitute for "
        "T074's mid-campaign dry-run** — that run, over the current corpus with every Phase 3-6 "
        "production in place, is what T071/T072 actually author against. This section exists so "
        "the worklist's SHAPE (grouped by datasheet, real line ordinals) is proven before that "
        "live run supplies the current, authoritative list.",
        "",
        f"**{worklist.total_rows} `OPT-UNPARSED` rows across {worklist.total_datasheets} "
        "datasheets, pre-008 baseline:**",
        "",
    ]
    if worklist.rows_by_datasheet:
        lines += [
            f"`{datasheet_id}`: lines {', '.join(str(line) for line in rows)}"
            for datasheet_id, rows in worklist.rows_by_datasheet.items()
        ]
    else:
        lines.append("(none)")
    lines.append("")
    return "\n".join(lines)


@dataclass(frozen=True, slots=True)
class PublishedSnapshotEvidence:
    """The three committed sources T001(b)/(c)/T003/T004 read, and nothing else."""

    rules_version_id: str
    snapshot: CuratedSnapshot
    findings: tuple[Mapping[str, object], ...]


def load_published_snapshot_evidence(
    root: Path, *, edition_code: str, manifest_relative_path: str = "site/manifest.json"
) -> PublishedSnapshotEvidence | None:
    """The previous published version's curated tree and retained report, or `None`.

    `None` when either is absent — a fresh checkout with no history, or a `--fixtures` rehearsal
    with no `data/`/`site/`/`reports/` at all — so this section is additive and never breaks a run
    that has nothing to read. Uses `previous_published_version`, the exact function
    `check_option_ratchet`'s own prior-snapshot resolution uses, so this measurement asks the
    identical question production code asks.
    """
    rules_version_id = previous_published_version(root / manifest_relative_path)
    if rules_version_id is None:
        return None
    snapshot = read_curated_tree(root / "data" / edition_code)
    if snapshot is None:
        return None
    report_path = root / "reports" / rules_version_id / "report.json"
    if not report_path.is_file():
        return None
    document = json.loads(report_path.read_text(encoding="utf-8"))
    findings = document.get("findings", [])
    if not isinstance(findings, list):
        findings = []
    return PublishedSnapshotEvidence(
        rules_version_id=rules_version_id,
        snapshot=snapshot,
        findings=tuple(f for f in findings if isinstance(f, Mapping)),
    )


def render_snapshot_sections(
    evidence: PublishedSnapshotEvidence,
    *,
    excluded: ExcludedPopulations,
    zero_group: ZeroGroupBreakdown,
    census: ConditionalBlockingCensus,
) -> str:
    """T001(b), T001(c), T003, T004 — rendered as their own Markdown sections. Counts and
    datasheet ids only; no source sentence appears anywhere below."""
    lines = [
        "",
        "## Zero-group breakdown and card-shape collapse (T001(b)/(c))",
        "",
        f"Read from the previous published version's own retained state: `data/` as of "
        f"`{evidence.rules_version_id}` and `reports/{evidence.rules_version_id}/report.json`. "
        "Not a live acquisition (see this report's methodology note) — the pipeline's own "
        "already-governed output for the corpus in question.",
        "",
        "| Population | Datasheets | Distinct card shapes |",
        "|---|---:|---:|",
        f"| `wargearOptionState=partial`, zero option groups (US1) | "
        f"{zero_group.zero_group_datasheets} | {zero_group.zero_group_shapes} |",
        f"| `wargearOptionState=partial`, some option groups (US2) | "
        f"{zero_group.some_group_datasheets} | {zero_group.some_group_shapes} |",
        "",
        "## Excluded populations (T004)",
        "",
        "Never counted as unresolved work by any task in this feature.",
        "",
        f"**Item-constraint vocabulary gap** (`docs/follow-ups.md` item 15) — "
        f"{len(excluded.item_constraint_vocabulary_gap)} datasheets, `CST-UNPARSED` and no "
        "`OPT-UNPARSED` finding at all:",
        "",
        (
            f"`{', '.join(excluded.item_constraint_vocabulary_gap)}`"
            if excluded.item_constraint_vocabulary_gap
            else "(none)"
        ),
        "",
        f"**No option state at all** (the source was never consulted; data-model.md §3's fourth "
        f"state) — {len(excluded.no_option_state_at_all)} datasheets:",
        "",
        (
            f"`{', '.join(excluded.no_option_state_at_all)}`"
            if excluded.no_option_state_at_all
            else "(none)"
        ),
        "",
        "## Conditional-blocking census (T003, sizes Open Decision O2)",
        "",
        "| `OPT-UNPARSED` rows | Datasheets carrying one | Single-row datasheets |",
        "|---:|---:|---:|",
        f"| {census.unparsed_rows_total} | {census.unparsed_row_datasheets} | "
        f"{census.single_row_datasheets} |",
        "",
        "Row-count histogram (rows unparsed on one datasheet -> how many datasheets):",
        "",
        "| Rows | Datasheets |",
        "|---:|---:|",
    ]
    lines += [f"| {rows} | {count} |" for rows, count in census.row_count_histogram.items()]
    lines += [
        "",
        f"**Estimate, not a measurement** (this report's methodology note explains why an exact "
        f"per-row diagnosis is not available in this environment): of the "
        f"{census.single_row_datasheets} single-unparsed-row datasheets, between "
        f"**{census.estimate_low}** and **{census.estimate_high}** are plausibly blocked *only* "
        f"by a `refused_conditional_or_equipment_qualified` row that no production or override may "
        f"legitimately close (FR-006, O2) — bounded by the measured "
        f"{census.measured_conditional_rows} conditional rows of "
        f"{census.measured_total_unparsed_rows} total unparsed (the diagnosis-class run this "
        "figure is carried forward from; see methodology note) applied to the single-row "
        "population, and by simple concentration.",
        "",
        f"**Compared against SC-002's headroom of {census.sc002_headroom}** (a gain of 126 "
        "datasheets is needed from a partial population of 162, of which 15 are excluded by the "
        "spec as the item-constraint vocabulary gap, leaving 147 addressable and only 126 of "
        "those needing to close): "
        + (
            f"**even the low end of the estimate ({census.estimate_low}) exceeds the headroom "
            f"({census.sc002_headroom})** — this report's own reading is that SC-002's 98% is "
            "not reachable as written without either the override path closing the gap (which "
            "O2 rules out for genuinely conditional rows) or a restated ceiling, which this "
            "report states as its own finding rather than rounding it away — see T014's "
            "decision package."
            if census.estimate_low > census.sc002_headroom
            else (
                f"the estimate range spans the headroom exactly "
                f"({census.estimate_low}-{census.estimate_high} against a headroom of "
                f"{census.sc002_headroom}) — inconclusive at this resolution, stated as such "
                "rather than rounded either way — see T014's decision package."
                if census.estimate_high > census.sc002_headroom
                else "the full estimate range stays within the headroom — SC-002's 98% reads as "
                "reachable on this evidence, subject to T074's real-corpus confirmation — see "
                "T014's decision package."
            )
        ),
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover - process entry point
    raise SystemExit(main())
