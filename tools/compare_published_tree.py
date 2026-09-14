#!/usr/bin/env python3
# AI-Assisted: Claude Code (model: Claude Opus 5) - Built for 010 R6: the CSV-sourced candidate
# build publishes datasheet JSON that differs in content from the published tree, and no tool in
# this repository compared the two field by field. Roster-identity assertions answer "are the same
# datasheets present"; nothing answered "do the shared ones say the same thing". This does, and it
# only ever counts - it is a measurement that informs a cutover decision, never a gate, so it
# exits 0 whatever it finds.
"""Field-level parity between a candidate data tree and the published one.

::

    python tools/compare_published_tree.py --published data --candidate <scratch>/out/data

What it compares, and the reasoning behind each rule:

* **Datasheets only**, keyed by their path under ``factions/``. Detachments and enhancements are
  a separate question with a separate shape; mixing them would blur the one count that matters.
* **``provenance``, ``pricing_confidence`` and every ``costs[].source_acquisition_id`` are
  stripped before the identity test.** Those record *how* a build ran, not what it published:
  they differ between any two runs, and leaving them in would make every datasheet differ and the
  report worthless.
* **Weapons pair by ``(name.casefold(), is_melee)``**, models by position, keywords by
  ``keyword.casefold()``. Two sources order their rows differently; an ordering difference is not
  a content difference and must not be reported as one.
* **A printed-suffix difference is not a content difference.** A skill of ``'3+'`` against ``'3'``
  and a range of ``'12"'`` against ``'12'`` are the same characteristic with and without its
  printed notation. They are counted under ``weapon_format_only`` and deliberately *not* under
  ``weapon_field_diffs``, because a cutover reading that conflates the two reports a stat change
  the candidate never made.

**No name, keyword or description ever reaches the output.** The markdown carries counts, field
names, and - for ``weapon_field_diffs`` - up to three sample value pairs per field, and a sample
is the literal value only for the numeric/stat fields whose vocabulary is shapes like ``'3+'``.
Every other field samples as the constant ``"<text>"``.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

PROG: Final = "compare_published_tree.py"

#: Recorded by the build, not published by the source: identical inputs produce different values
#: here on every run, so they are removed before anything is compared.
EXCLUDED_TOP_LEVEL: Final = frozenset({"provenance", "pricing_confidence"})
EXCLUDED_COST_FIELD: Final = "source_acquisition_id"

WEAPON_FIELDS: Final = (
    # Weapons *pair* case-insensitively, so a paired pair whose printed names differ differs by
    # case alone - and that difference must still be counted rather than absorbed by the
    # pairing rule, which is otherwise a comparison that cannot see what it matched on.
    "name",
    "line",
    "range",
    "attacks",
    "skill",
    "strength",
    "armour_penetration",
    "damage",
    "ability_keywords",
)
MODEL_FIELDS: Final = (
    "name",
    "line",
    "movement",
    "toughness",
    "save",
    "invuln_save",
    "wounds",
    "leadership",
    "objective_control",
    "base_size",
)

#: The fields whose whole vocabulary is stat shapes - ``'3+'``, ``'12"'``, ``'32mm'``, ``'D6'``.
#: Only these may appear verbatim in a sample pair; everything else samples as ``"<text>"``,
#: because everything else is or may contain the publisher's wording.
SHAPE_FIELDS: Final = frozenset(
    {
        "skill",
        "range",
        "invuln_save",
        "base_size",
        "attacks",
        "strength",
        "armour_penetration",
        "damage",
    }
)

#: Fields where one side prints the notation and the other does not. Checked for a
#: digits-identical pair *before* the pair is called a content difference.
FORMAT_SENSITIVE_FIELDS: Final = ("skill", "range")

MAX_SAMPLES: Final = 3

#: Exit code for an argument that cannot be compared at all. The brief's "exit 0 always" binds
#: the *measurement verdict* - no reading, however bad, is a failure - and not an argument error.
USAGE_EXIT: Final = 2

#: Distinguishes "the key is not there" from "the key is there and null". Comparing `.get(key)`
#: on both sides conflates them and hides a real difference.
_ABSENT: Final = object()


@dataclass(slots=True)
class ParityReport:
    """Everything the comparison found, as counts. Nothing here can hold a cell value."""

    shared: int = 0
    only_published: int = 0
    only_candidate: int = 0
    identical: int = 0
    top_level: dict[str, int] = field(default_factory=dict)
    keywords_case_only: int = 0
    keywords_set_differs: int = 0
    keywords_missing: int = 0
    keywords_extra: int = 0
    ability_keys_only_published: dict[str, int] = field(default_factory=dict)
    ability_keys_only_candidate: dict[str, int] = field(default_factory=dict)
    weapons_paired: int = 0
    weapons_only_published: dict[str, int] = field(default_factory=dict)
    weapons_only_candidate: dict[str, int] = field(default_factory=dict)
    weapon_field_diffs: dict[str, int] = field(default_factory=dict)
    weapon_format_only: dict[str, int] = field(default_factory=dict)
    models_count_differs: int = 0
    model_field_diffs: dict[str, int] = field(default_factory=dict)
    names_case_only: int = 0
    names_differ: int = 0
    weapon_samples: dict[str, list[tuple[str, str]]] = field(default_factory=dict)

    @property
    def weapon_profiles_published(self) -> int:
        """Profiles the published tree carries on shared datasheets: paired plus its surplus."""
        return self.weapons_paired + sum(self.weapons_only_published.values())

    @property
    def weapon_profiles_candidate(self) -> int:
        """The same for the candidate. Printed because the headline question is "how many rows
        did the candidate stop publishing", and a paired count alone cannot answer it."""
        return self.weapons_paired + sum(self.weapons_only_candidate.values())

    def to_markdown(self) -> str:
        """Render the measurement. Counts, field names and stat shapes only."""
        lines = [
            "<!-- AI-Assisted: Claude Code (model: Claude Opus 5) - Generated by "
            "tools/compare_published_tree.py (010 R6). -->",
            "# Published-vs-candidate field parity",
            "",
            "Measurement only: this tool gates nothing and exits 0 whatever it finds.",
            "",
            "## Roster",
            "",
            "| Shared | Only published | Only candidate | Identical (after exclusions) |",
            "|---:|---:|---:|---:|",
            f"| {self.shared} | {self.only_published} | {self.only_candidate} | {self.identical} |",
            "",
            "Excluded before the identity test: `provenance`, `pricing_confidence`, "
            "`costs[].source_acquisition_id`.",
            "",
            "## Top-level keys",
            "",
            "Shared datasheets differing on each key.",
            "",
            "| Key | Datasheets differing |",
            "|---|---:|",
        ]
        lines += [
            f"| `{key}` | {count} |"
            for key, count in sorted(self.top_level.items(), key=lambda kv: (-kv[1], kv[0]))
        ]
        lines += [
            "",
            "## Name",
            "",
            f"- Case-only: {self.names_case_only}",
            f"- Differs: {self.names_differ}",
            "",
            "## Keywords",
            "",
            f"- Case-only difference: {self.keywords_case_only}",
            f"- Set differs: {self.keywords_set_differs}",
            f"- Missing from candidate: {self.keywords_missing}",
            f"- Extra in candidate: {self.keywords_extra}",
            "",
            "## Ability-key bindings",
            "",
            "Counted per binding over shared datasheets, by key prefix.",
            "",
            "| Prefix | Only published | Only candidate |",
            "|---|---:|---:|",
        ]
        prefixes = sorted(
            set(self.ability_keys_only_published) | set(self.ability_keys_only_candidate)
        )
        lines += [
            f"| `{prefix}` | {self.ability_keys_only_published.get(prefix, 0)} | "
            f"{self.ability_keys_only_candidate.get(prefix, 0)} |"
            for prefix in prefixes
        ]
        lines += [
            "",
            "## Weapon profiles",
            "",
            f"- Profiles on shared datasheets: published {self.weapon_profiles_published}, "
            f"candidate {self.weapon_profiles_candidate}",
            f"- Paired: {self.weapons_paired}",
            f"- Only published: {_render_counts(self.weapons_only_published)}",
            f"- Only candidate: {_render_counts(self.weapons_only_candidate)}",
            "",
            "### Field differences among paired profiles",
            "",
            "`format only` is a printed-suffix difference with identical digits "
            '(`3+`/`3`, `12"`/`12`) and is excluded from the content column.',
            "",
            "| Field | Content differs | Format only | Sample pairs (published, candidate) |",
            "|---|---:|---:|---|",
        ]
        fields_seen = sorted(
            set(self.weapon_field_diffs) | set(self.weapon_format_only),
            key=lambda key: (-self.weapon_field_diffs.get(key, 0), key),
        )
        for key in fields_seen:
            samples = ", ".join(
                f"(`{published}`, `{candidate}`)"
                for published, candidate in self.weapon_samples.get(key, [])
            )
            lines.append(
                f"| `{key}` | {self.weapon_field_diffs.get(key, 0)} | "
                f"{self.weapon_format_only.get(key, 0)} | {samples or '-'} |"
            )
        lines += [
            "",
            "## Model profiles",
            "",
            f"- Shared datasheets whose model count differs: {self.models_count_differs}",
            "",
            "| Field | Profiles differing |",
            "|---|---:|",
        ]
        lines += [
            f"| `{key}` | {count} |"
            for key, count in sorted(self.model_field_diffs.items(), key=lambda kv: (-kv[1], kv[0]))
        ]
        lines.append("")
        return "\n".join(lines)


def _render_counts(counts: dict[str, int]) -> str:
    return ", ".join(f"{key} {value}" for key, value in sorted(counts.items())) or "none"


def _bump(counts: dict[str, int], key: str, amount: int = 1) -> None:
    if amount:
        counts[key] = counts.get(key, 0) + amount


class UsageError(Exception):
    """An argument that cannot be compared at all - not a reading, however bad.

    Kept distinct from every measurement outcome because the two must never share an exit code:
    a comparison that finds total divergence is a *result*, and a root that points at nothing is
    a mistake in the invocation.
    """


def _data_dir(root: Path) -> Path:
    """Strip one leading ``wh40k-*`` version directory when there is exactly one.

    The two roots are named by different runs and may or may not carry the version directory;
    keying paths relative to it is what makes ``data/wh40k-11e/...`` and a scratch build
    comparable at all.

    Two or more version directories is an ambiguity, and it is *named* rather than resolved by
    picking one: silently choosing the first would compare one edition's tree against another's
    and report the difference as a build defect.
    """
    versions = sorted(child for child in root.glob("wh40k-*") if child.is_dir())
    if len(versions) > 1:
        raise UsageError(
            f"{root} holds {len(versions)} wh40k-* version directories; "
            "point --published/--candidate at exactly one"
        )
    return versions[0] if versions else root


def _load_tree(root: Path) -> dict[str, Any]:
    """``<faction>/<...>/<ds>.json -> payload`` for every datasheet under ``factions/``.

    A root that yields no datasheets raises rather than returning ``{}``. This is CLAUDE.md
    trap 1 on the output side: an empty tree renders a complete report of zeros, which is
    indistinguishable from a genuine comparison that found nothing wrong, and a mistyped path
    would read as parity.
    """
    factions = _data_dir(root) / "factions"
    tree: dict[str, Any] = {}
    if factions.is_dir():
        for path in sorted(factions.rglob("*.json")):
            if not path.name.startswith("ds-"):
                continue
            payload = json.loads(path.read_text(encoding="utf-8"))
            tree[path.relative_to(factions).as_posix()] = payload
    if not tree:
        raise UsageError(f"{root} holds no datasheets under factions/; nothing to compare")
    return tree


def _strip_excluded(payload: Any) -> dict[str, Any]:
    """Remove the build-recorded fields, returning a copy. The input is never mutated."""
    stripped = {key: value for key, value in dict(payload).items() if key not in EXCLUDED_TOP_LEVEL}
    costs = stripped.get("costs")
    if isinstance(costs, list):
        stripped["costs"] = [
            {key: value for key, value in dict(cost).items() if key != EXCLUDED_COST_FIELD}
            if isinstance(cost, dict)
            else cost
            for cost in costs
        ]
    return stripped


def _rows(payload: Any, key: str) -> list[dict[str, Any]]:
    rows = payload.get(key)
    return [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []


def _digits(value: Any) -> str:
    return "".join(char for char in str(value) if char.isdigit())


def _is_format_only(field_name: str, published: Any, candidate: Any) -> bool:
    """True when the pair differs only in printed notation: same digits, different text."""
    if field_name not in FORMAT_SENSITIVE_FIELDS:
        return False
    if published is None or candidate is None:
        return False
    digits = _digits(published)
    return bool(digits) and digits == _digits(candidate)


def _shape(field_name: str, value: Any) -> str:
    """A sample that may be printed. Verbatim for stat fields, opaque for everything else."""
    if value is None:
        return "<none>"
    if field_name in SHAPE_FIELDS and isinstance(value, str):
        return value
    if isinstance(value, bool | int | float):
        return str(value)
    return "<text>"


def _weapon_kind(weapon: dict[str, Any]) -> str:
    return "melee" if weapon.get("is_melee") else "ranged"


def _group_weapons(weapons: list[dict[str, Any]]) -> dict[tuple[str, bool], list[dict[str, Any]]]:
    grouped: dict[tuple[str, bool], list[dict[str, Any]]] = {}
    for weapon in weapons:
        key = (str(weapon.get("name", "")).casefold(), bool(weapon.get("is_melee")))
        grouped.setdefault(key, []).append(weapon)
    return grouped


def _compare_weapons(published: Any, candidate: Any, report: ParityReport) -> None:
    """Pair by ``(name.casefold(), is_melee)``, zip in order, classify each field difference."""
    left = _group_weapons(_rows(published, "weapons"))
    right = _group_weapons(_rows(candidate, "weapons"))
    for key in sorted(set(left) | set(right)):
        lhs = left.get(key, [])
        rhs = right.get(key, [])
        paired = min(len(lhs), len(rhs))
        report.weapons_paired += paired
        surplus_sides = (
            (lhs[paired:], report.weapons_only_published),
            (rhs[paired:], report.weapons_only_candidate),
        )
        for surplus, counts in surplus_sides:
            for weapon in surplus:
                _bump(counts, _weapon_kind(weapon))
        for published_weapon, candidate_weapon in zip(lhs[:paired], rhs[:paired], strict=True):
            _compare_weapon_pair(published_weapon, candidate_weapon, report)


def _compare_weapon_pair(
    published: dict[str, Any], candidate: dict[str, Any], report: ParityReport
) -> None:
    for name in WEAPON_FIELDS:
        published_value = published.get(name)
        candidate_value = candidate.get(name)
        if published_value == candidate_value:
            continue
        if _is_format_only(name, published_value, candidate_value):
            # Counted here and *only* here: a pair called format-only is deliberately absent from
            # weapon_field_diffs, so the content column never reports a stat the build kept.
            _bump(report.weapon_format_only, name)
            continue
        _bump(report.weapon_field_diffs, name)
        samples = report.weapon_samples.setdefault(name, [])
        if len(samples) < MAX_SAMPLES:
            samples.append((_shape(name, published_value), _shape(name, candidate_value)))


def _compare_models(published: Any, candidate: Any, report: ParityReport) -> None:
    """Pair by position, and only when the counts agree - position means nothing otherwise."""
    lhs = _rows(published, "models")
    rhs = _rows(candidate, "models")
    if len(lhs) != len(rhs):
        report.models_count_differs += 1
        return
    for published_model, candidate_model in zip(lhs, rhs, strict=True):
        for name in MODEL_FIELDS:
            if published_model.get(name) != candidate_model.get(name):
                _bump(report.model_field_diffs, name)


def _compare_keywords(published: Any, candidate: Any, report: ParityReport) -> None:
    """Case-insensitively equal sets whose printed text differs are a case-only difference."""
    published_raw = [str(row.get("keyword", "")) for row in _rows(published, "keywords")]
    candidate_raw = [str(row.get("keyword", "")) for row in _rows(candidate, "keywords")]
    left_folded = sorted(value.casefold() for value in published_raw)
    right_folded = sorted(value.casefold() for value in candidate_raw)
    if left_folded == right_folded:
        # Equal as *multisets*, not merely as sets. A side carrying the same keyword twice has
        # an equal set and a different list, and filing that as "case only" asserts a
        # capitalisation difference that was never checked - it is a count difference.
        if sorted(published_raw) != sorted(candidate_raw):
            report.keywords_case_only += 1
        return
    report.keywords_set_differs += 1
    report.keywords_missing += len(set(left_folded) - set(right_folded))
    report.keywords_extra += len(set(right_folded) - set(left_folded))


def _keys(payload: Any) -> set[str]:
    keys = payload.get("ability_keys")
    return {str(key) for key in keys} if isinstance(keys, list) else set()


def _compare_ability_keys(published: Any, candidate: Any, report: ParityReport) -> None:
    """Set difference of the **full** ``prefix:slug`` strings, bucketed by prefix.

    Per datasheet, so a key missing on three datasheets counts three times - bindings, not
    distinct keys. The difference is taken over the whole key and never over a per-prefix
    *count*: a datasheet holding three ``core:`` keys on each side whose slugs all differ has a
    count difference of zero and a set difference of three, and reporting zero there is a claim
    of parity the comparison never made.
    """
    left = _keys(published)
    right = _keys(candidate)
    for key in left - right:
        _bump(report.ability_keys_only_published, key.split(":", 1)[0])
    for key in right - left:
        _bump(report.ability_keys_only_candidate, key.split(":", 1)[0])


def _compare_names(published: Any, candidate: Any, report: ParityReport) -> None:
    left = str(published.get("name", ""))
    right = str(candidate.get("name", ""))
    if left == right:
        return
    if left.casefold() == right.casefold():
        report.names_case_only += 1
    else:
        report.names_differ += 1


def compare_trees(published: Path, candidate: Path) -> ParityReport:
    """Compare every datasheet the two trees share, field by field."""
    left = _load_tree(published)
    right = _load_tree(candidate)
    shared = sorted(set(left) & set(right))

    report = ParityReport(
        shared=len(shared),
        only_published=len(set(left) - set(right)),
        only_candidate=len(set(right) - set(left)),
    )
    for relative in shared:
        published_payload = _strip_excluded(left[relative])
        candidate_payload = _strip_excluded(right[relative])
        if published_payload == candidate_payload:
            report.identical += 1
        for key in set(published_payload) | set(candidate_payload):
            # `_ABSENT`, not `.get(key)`: a key present as null on one side and absent on the
            # other makes the datasheet non-identical, and comparing two `None`s would leave
            # that difference counted in `identical` yet named in no row of the table.
            if published_payload.get(key, _ABSENT) != candidate_payload.get(key, _ABSENT):
                _bump(report.top_level, key)
        _compare_names(published_payload, candidate_payload, report)
        _compare_keywords(published_payload, candidate_payload, report)
        _compare_ability_keys(published_payload, candidate_payload, report)
        _compare_weapons(published_payload, candidate_payload, report)
        _compare_models(published_payload, candidate_payload, report)
    return report


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Measure field-level parity between a published data tree and a candidate.",
    )
    parser.add_argument("--published", type=Path, required=True, help="published data root")
    parser.add_argument("--candidate", type=Path, required=True, help="candidate data root")
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Sequence[str] | None = None) -> int:
    """Print the markdown and exit 0. This tool measures; it never gates."""
    args = _parse_args(argv)
    for label, root in (("--published", args.published), ("--candidate", args.candidate)):
        if not root.is_dir():
            print(f"{PROG}: {label} is not a directory", file=sys.stderr)
            return USAGE_EXIT
    try:
        report = compare_trees(args.published, args.candidate)
    except UsageError as exc:
        # Nothing is printed to stdout on this path. A report of zeros on a mis-aimed root is
        # the failure mode this branch exists to prevent, so the diagnostic replaces it rather
        # than accompanying it.
        print(f"{PROG}: {exc}", file=sys.stderr)
        return USAGE_EXIT
    print(report.to_markdown())
    return 0


if __name__ == "__main__":  # pragma: no cover - process entry point
    raise SystemExit(main())
