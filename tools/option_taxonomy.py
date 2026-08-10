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
import re
import sys
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

from pipeline.acquire.detail_source import acquire_detail, read_detail
from pipeline.acquire.http import AcquisitionError
from pipeline.config import ConfigError, PipelineConfig, load_config, repo_root
from pipeline.exit_codes import ExitCode
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
        "Pure grant, no replacement — `... can have INT <ITEM>`",
        stem=re.compile(r"\bcan (?:each )?have\b", _I),
        absent=re.compile(r"\breplaced\b", _I),
    ),
    # Ordered ahead of class 11 deliberately. A conditional stem that opens an `<li>` list —
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
    ("sublist", "carries an `<li>` sub-list"),
    ("following", "stem ends `one of the following:`"),
    ("multi_replaced", "multi-item REPLACED set (FR-005)"),
    ("multi_granted", "multi-item GRANTED bundle (FR-006)"),
    ("distributive", "distributive `can each` (FR-004, `isPerModel`)"),
    ("scoped_max", "`Up to INT <MODEL>` — an explicit eligibility cap (`eligibleMaxCount`)"),
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

#: A conjunction joining two counted items — `INT <ITEM> and INT <ITEM>` — on the granted side.
#: The leading count is what distinguishes a bundle from an item whose own name contains `and`.
_COUNTED_CONJUNCT: Final = re.compile(r"^\d+\s+.+?\s+and\s+\d+\s+\S", _I)

#: Research D1d's first silent-failure class, over the rows that **do** parse: the whole object
#: clause collapsed into one choice `name`, so the bundle is conflated rather than truncated and
#: the choice ships unlinked (006 task T018 decomposes these without renaming them — the O1
#: Ruling).
_CONFLATED_NAME: Final = re.compile(r"\band\s+\d+\s+\S|\b\S+\s+(?:and|or)\s+\S+", _I)

#: Research D1d's second: a group-level select quantifier in the stem's post-verb remainder,
#: discarded today whenever an `<li>` list exists, so the group publishes as *pick any number*
#: where the source says *pick up to N* (006 task T019 populates `min_choices`/`max_choices`).
_SELECT_QUANTIFIER: Final = re.compile(
    r"\b(?:up to \d+ of the following|\d+ different\b.*\bfrom the following)", _I
)


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
            parsed = parse_row(description)
            if parsed is None:
                unparsed_per_faction[faction_id] = unparsed_per_faction.get(faction_id, 0) + 1
                partial_datasheets.setdefault(faction_id, set()).add(datasheet_id)
                class_counts[classify(stem)] += 1
                for feature in features_of(stem, items):
                    feature_counts[feature] += 1
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
        class_labels={rule.key: rule.label for rule in _CLASSES},
    )


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
    return parser.parse_args(list(argv) if argv is not None else None)


def _summary_line(report: TaxonomyReport) -> str:
    top = sorted(report.classes.items(), key=lambda item: (-item[1], item[0]))[:1]
    leader = f"{top[0][0]} ({top[0][1]})" if top and top[0][1] else "none"
    return (
        f"{PROG}: {report.unparsed} of {report.rows} option rows unparsed "
        f"({report.ratio:.1%}) over {report.datasheets} datasheets; largest class {leader}"
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    root = args.repo or repo_root()

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
    if args.print_only:
        print(rendered)
    else:
        destination = args.out or (root / REPORTS_DIR / f"{report.generated_at[:10]}.md")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"{PROG}: wrote {destination}")

    print(_summary_line(report))
    return int(ExitCode.SUCCESS)


def iter_class_keys() -> Iterable[str]:
    """Every taxonomy class key, in report order — a convenience for tests and reports."""
    return sorted((rule.key for rule in _CLASSES), key=_class_sort_key)


if __name__ == "__main__":  # pragma: no cover - process entry point
    raise SystemExit(main())
